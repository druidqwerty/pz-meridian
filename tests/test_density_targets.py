"""Reject stale furnishing metadata; do not let occupied squares become observers."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from density_targets import free_room_points, match_room, walk_pair, programme_candidates


class DensityTargetSafety(unittest.TestCase):
    def setUp(self):
        self.db = {'floor': {'solidfloor': 'true'},
                   'cabinet': {'IsMoveAble': 'true'},
                   'stair': {'stairsTW': 'true'},
                   'wall': {'collideW': 'true', 'WallW': 'true'}}
        self.data = dict(rooms=[dict(name='office', level=0, rects=[(10, 12, 14, 10)])],
                         tiles={}, room_ids={})
        for x in range(10, 24):
            for y in range(12, 22):
                self.data['tiles'][x, y, 0] = ['floor']
                self.data['room_ids'][x, y, 0] = 0

    def test_occupied_centre_and_stairs_are_not_observer_or_walk_destination(self):
        self.data['tiles'][17, 17, 0].append('cabinet')
        self.data['tiles'][16, 17, 0].append('stair')
        free = free_room_points(self.data, 0, self.db)
        self.assertNotIn((17, 17), free)
        self.assertNotIn((16, 17), free)
        start, end, length = walk_pair(self.data, 0, self.db)
        self.assertIn(start, free)
        self.assertIn(end, free)
        self.assertGreaterEqual(length, 4)

    def test_walk_does_not_cross_a_wall_inside_same_room_definition(self):
        for y in range(12, 22):
            self.data['tiles'][17, y, 0].append('wall')
        start, end, length = walk_pair(self.data, 0, self.db)
        self.assertEqual(start[0] >= 17, end[0] >= 17)

    def test_manifest_world_rect_is_bound_to_actual_native_room_and_loot_role(self):
        receipt = dict(rect=[266, 524, 14, 10], z=0, lootRole='office')
        self.assertEqual(match_room(self.data, receipt, 1, 2), 0)
        for change in (dict(lootRole='classroom'), dict(z=1), dict(rect=[267, 524, 14, 10])):
            with self.assertRaises(ValueError):
                match_room(self.data, receipt | change, 1, 2)

    def test_native_loot_role_cannot_mislabel_nursery_or_restaurant_kitchen(self):
        def entry(loot, purpose):
            return ([1, 2], {}, dict(lootRole=loot, purpose=purpose, z=0, rect=[260, 520, 20, 20]))
        nursery = entry('classroom', 'nursery')
        classroom = entry('classroom', 'classroom')
        kitchen = entry('kitchen', 'restaurantkitchen')
        dining = entry('hall', 'dining')
        entries = [nursery, kitchen, classroom, dining]
        self.assertEqual(programme_candidates(entries, {'classroom'}, {'classroom'}, False,
                                              [0, 0, 1000, 1000]), [classroom])
        self.assertEqual(programme_candidates(entries, {'hall', 'livingroom', 'kitchen'}, {'dining'}, False,
                                              [0, 0, 1000, 1000]), [dining])
        missing = entry('classroom', None)
        self.assertEqual(programme_candidates([missing], {'classroom'}, {'classroom'}, False,
                                              [0, 0, 1000, 1000]), [])


if __name__ == '__main__':
    unittest.main()
