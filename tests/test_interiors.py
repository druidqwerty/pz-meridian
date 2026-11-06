"""Interior acceptance against independent installed B42 properties and codec."""
from pathlib import Path
import sys, tempfile, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from furnishing import furnish_room
from furniture_orientation import FACING, BED_GROUPS, SOFA_GROUPS, MEDICAL_GROUP
from room_lighting import place_room_lighting
from map_binary import write_cell, read_cell
from test_architecture import GAME, sprites


@unittest.skipUnless(GAME.exists(), 'Requires owner-installed B42 property oracle')
class NativeInteriorAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sprites()

    def test_curated_fronts_match_native_facing_and_complete_sprite_grids(self):
        for key, directions in FACING.items():
            for direction, sprite in directions.items():
                self.assertEqual(self.db[sprite]['Facing'], direction, (key, sprite))
                self.assertNotIn('SpriteGridPos', self.db[sprite])
        for group in [*BED_GROUPS.values(), *SOFA_GROUPS.values(), MEDICAL_GROUP]:
            for x, y, sprite in group:
                self.assertEqual(self.db[sprite]['SpriteGridPos'], f'{x},{y}', sprite)

    def test_blocked_door_approach_never_truncates_bed_and_seats_face_table(self):
        from architecture import TILES
        blocked = {(11, 10), (11, 11), (12, 10), (12, 11)}
        result = list(furnish_room('bedroom', 10, 10, 12, 10, 0, TILES, blocked))
        self.assertFalse({(x, y) for x, y, _ in result} & blocked)
        by_pos = {(x, y): sprite for x, y, sprite in result if 'bedding' in sprite}
        for (x, y), sprite in by_pos.items():
            if sprite == 'furniture_bedding_01_9':
                self.assertEqual(by_pos[x, y+1], 'furniture_bedding_01_8')
            else:
                self.assertEqual(by_pos[x, y-1], 'furniture_bedding_01_9')
        kitchen = {(x, y): s for x, y, s in
                   furnish_room('kitchen', 10, 10, 12, 10, 1, TILES)}
        # South-wall kitchen counter/appliances face into the room, uniformly.
        self.assertEqual(self.db[kitchen[11, 10]]['Facing'], 'S')
        self.assertEqual(self.db[kitchen[12, 10]]['Facing'], 'S')
        self.assertEqual(self.db[kitchen[13, 10]]['Facing'], 'S')
        self.assertEqual(self.db[kitchen[12, 18]]['Facing'], 'N')
        self.assertEqual(self.db[kitchen[13, 17]]['Facing'], 'W')

    def test_each_room_gets_real_switch_circuit_and_luminous_fixture_roundtrip(self):
        tiles = {(x, y, 0): ['floors_interior_tilesandwood_01_40']
                 for x in range(20, 28) for y in range(20, 27)}
        for x in range(20, 28):
            tiles[x, 20, 0].append('walls_exterior_house_02_17')
        room = dict(name='livingroom', level=0, rects=[(20, 20, 8, 7)], objects=[])
        proofs = place_room_lighting(tiles, room)
        switches = [p for p in proofs if p['kind'] == 'switch']
        lamps = [p for p in proofs if p['kind'] == 'lamp']
        self.assertEqual(len(switches), 1)
        self.assertGreaterEqual(len(lamps), 1)
        sx, sy = switches[0]['x'], switches[0]['y']
        self.assertEqual(room['objects'], [(7, sx, sy)])
        for proof in proofs:
            props = self.db[proof['sprite']]
            self.assertIn('lightswitch', props)
            self.assertIn('attachedN', props)
            if proof['kind'] == 'lamp':
                self.assertGreater(int(props['LightRadius']), 0)
                self.assertGreater(int(props['lightR']), 0)
        before = {p: list(names) for p, names in tiles.items()}
        place_room_lighting(tiles, room)
        self.assertEqual(tiles, before, 'Repeated decoration duplicates lights')
        with tempfile.TemporaryDirectory() as out:
            write_cell(out, 0, 0, tiles, [room], [[0]], 0)
            decoded = read_cell(out, 0, 0)
            self.assertEqual(decoded['rooms'][0]['objects'], [(7, sx, sy)])


if __name__ == '__main__':
    unittest.main()
