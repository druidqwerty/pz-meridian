"""Independent collision/native metadata gates for all twelve surface entrances."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from bunker import build_bunker
from bunker_wayfinding import decorate
from test_architecture import GAME, sprites, reachable


@unittest.skipUnless(GAME.exists(), 'Requires locally installed B42 metadata')
class BunkerWayfinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.props = sprites()

    def test_all_native_entrances_preserve_stairs_and_open_routes(self):
        config = dict(minCX=188, maxCX=191, minCY=4, maxCY=7)
        for cx in range(188, 192):
            for cy in range(4, 8):
                if cx not in (188, 191) and cy not in (4, 7):
                    continue
                with self.subTest(cell=(cx, cy)):
                    tiles, rooms, buildings = {}, [], []
                    bunker = build_bunker(tiles, rooms, buildings, cx, cy, config)
                    before = copy.deepcopy(tiles)
                    result = decorate(tiles, cx, cy, bunker)
                    self.assertEqual(set(tiles), set(before), 'No floors or squares may be invented')
                    for x in range(128, 131):
                        for y, z in ((128, 0), (128, -1), (136, -1), (136, -2)):
                            self.assertEqual(tiles.get((x, y, z)), before.get((x, y, z)))
                    unknown = {name for names in tiles.values() for name in names} - self.props.keys()
                    self.assertFalse(unknown)
                    self.assertGreater(result['counts']['props'], 5)
                    self.assertEqual(result['counts']['signs'], 2)
                    seen, _ = reachable(tiles, self.props, (131, 143), 0)
                    self.assertIn((127, 128), seen, 'Door-to-upper-landing route blocked')
                    self.assertIn((127, 136), reachable(tiles, self.props, (131, 128), -1)[0])
                    decorated = copy.deepcopy(tiles)
                    decorate(tiles, cx, cy, bunker)
                    self.assertEqual(tiles, decorated, 'Repeat decoration must not accumulate props')


if __name__ == '__main__':
    unittest.main()
