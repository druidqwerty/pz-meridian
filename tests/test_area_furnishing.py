"""Purpose/density acceptance on actual layouts, not sprite-count snapshots."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from area_furnishing import plan_furnishing, world_reports
from architecture import KINDS, build_structure
from furniture_orientation import FACING


class AreaFurnishingAcceptance(unittest.TestCase):
    def test_vendored_planner_is_exact_hash_bound_pure_source(self):
        vendor = ROOT/'tools/native_b42'
        provenance = json.loads((vendor/'PROVENANCE.json').read_text())
        self.assertTrue((vendor/'LICENSE-PZ-MAP-TOOLS.txt').is_file())
        for entry in provenance['files']:
            content = (vendor/entry['path']).read_bytes()
            self.assertNotIn(b'\r\n', content)
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry['sha256'])
            upstream = ROOT.parent/'pz-map-tools/tools/native_b42'/entry['path']
            if upstream.exists():
                self.assertEqual(content, upstream.read_bytes().replace(b'\r\n', b'\n'))

    def test_large_kitchen_has_one_line_and_distributed_preparation_not_duplicates(self):
        props, report = plan_furnishing('kitchen', 10, 20, 23, 32, 2,
                                        programme='restaurantkitchen')
        self.assertEqual(report['policy'], 'zoned')
        self.assertTrue(report['accepted'], report)
        self.assertFalse(report['warnings'])
        counts = Counter(sprite for _, _, sprite in props)
        self.assertEqual(sum(counts[n] for n in FACING['oven'].values()), 1)
        self.assertEqual(sum(counts[n] for n in FACING['fridge'].values()), 1)
        activities = Counter(group['activity'] for group in report['groups'])
        self.assertEqual(activities['kitchen']+activities['kitchen_compact'], 1)
        self.assertGreater(activities['prep'], 2)
        self.assertLessEqual(report['largestEmptySquare']['side'], report['maxEmptySide'])
        self.assertTrue(any(y > 20+16 for _, y, _ in props))

    def test_all_actual_surface_layouts_accept_with_explicit_compact_corridor_policies(self):
        policies = Counter()
        for kind in KINDS:
            for seed in (0, 1, 2, 3):
                rec = build_structure({}, [], [], 24, 24, kind, seed)
                for report in rec['furnishing']:
                    policies[report['policy']] += 1
                    self.assertFalse(report['warnings'], (kind, seed, report))
                    if report['policy'] == 'zoned':
                        self.assertTrue(report['accepted'], (kind, seed, report))
                        self.assertTrue(report['densityAudited'])
                        self.assertTrue(report['connectedFloor'])
                        self.assertTrue(report['groups'])
                        self.assertEqual(report['attempts'][-1]['accepted'], True)
                    else:
                        self.assertIsNone(report['accepted'])
                        self.assertFalse(report['densityAudited'])
                        self.assertTrue(report['reason'])
        self.assertGreater(policies['zoned'], 500)
        self.assertTrue(policies['compact'] and policies['circulation'])

    def test_explicit_routes_and_solid_cache_do_not_receive_furniture(self):
        route = {(a, 28) for a in range(10, 42)}
        cache = {(40, 22)}
        props, report = plan_furnishing('office', 10, 20, 32, 24, 3,
                                        blocked=route, obstacles=cache)
        self.assertTrue(report['accepted'], report)
        self.assertFalse({(x, y) for x, y, _ in props} & (route | cache))
        self.assertTrue(report['connectedFloor'])

    def test_compact_masks_keep_complete_groups_away_from_solids_and_activity(self):
        solid = {(11, 20)}
        activity = {(15, 23), (15, 24)}
        props, report = plan_furnishing('bedroom', 10, 20, 8, 8,
                                        obstacles=solid, activity=activity)
        occupied = {(x, y) for x, y, _ in props}
        self.assertFalse(occupied & (solid | activity))
        self.assertFalse(occupied & {(x+dx, y+dy) for x, y in solid
                            for dx in (-1, 0, 1) for dy in (-1, 0, 1)})
        beds = {(x, y): s for x, y, s in props if 'furniture_bedding' in s}
        for (x, y), sprite in beds.items():
            partner = (x, y+1) if sprite.endswith('_9') else (x, y-1)
            self.assertIn(partner, beds)
        self.assertIsNone(report['accepted'])
        self.assertFalse(report['densityAudited'])
        with self.assertRaisesRegex(ValueError, 'Solid obstacles'):
            plan_furnishing('office', 10, 20, 8, 8,
                            blocked=solid, obstacles=solid)

    def test_surface_cache_is_planned_solid_not_a_post_plan_front_obstruction(self):
        tiles, rooms = {}, []
        rec = build_structure(tiles, rooms, [], 24, 24, 'visitor', 0)
        self.assertTrue(rec['caches'])
        fronts = dict(N=(0, -1), S=(0, 1), E=(1, 0), W=(-1, 0))
        directional = {sprite: fronts[direction] for key in
                       ('metal', 'shelves', 'dresser', 'counter', 'fridge', 'oven')
                       for direction, sprite in FACING[key].items()}
        for cx, cy, z in rec['caches']:
            # The cache's own native S front remains usable too.
            self.assertEqual(len(tiles[cx, cy+1, z]), 1)
            for (x, y, zz), layers in tiles.items():
                if zz != z or (x, y) == (cx, cy):
                    continue
                for sprite in layers:
                    if sprite in directional:
                        dx, dy = directional[sprite]
                        self.assertNotEqual((x+dx, y+dy), (cx, cy), sprite)
        self.assertTrue(all(report['accepted'] is not False
                            for report in rec['furnishing']))

    def test_cached_room_does_not_share_mutable_reports_and_world_shift_is_exact(self):
        props, first = plan_furnishing('office', 10, 20, 32, 24, 1)
        expected = json.loads(json.dumps(first))
        world_reports([first], 188, 4)
        first['groups'][0]['activity'] = 'damaged-by-caller'
        second_props, second = plan_furnishing('office', 10, 20, 32, 24, 1)
        self.assertEqual(props, second_props)
        self.assertEqual(second, expected)
        self.assertEqual(first['rect'][:2], [188*256+10, 4*256+20])
        self.assertEqual(first['largestEmptySquare']['x'],
                         expected['largestEmptySquare']['x']+188*256)

    def test_unsolved_large_domestic_room_is_not_silently_compact_or_accepted(self):
        with self.assertRaisesRegex(ValueError, 'oversized_domestic_room'):
            plan_furnishing('kitchen', 0, 0, 60, 20, 0)
        with self.assertRaisesRegex(ValueError, 'No furnishing programme'):
            plan_furnishing('madeup', 0, 0, 32, 24, 0)
        with self.assertRaisesRegex(ValueError, 'No furnishing programme'):
            plan_furnishing('madeup', 0, 0, 5, 5, 0)


if __name__ == '__main__':
    unittest.main()
