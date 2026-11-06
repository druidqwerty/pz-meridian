"""Negative controls: acceptance flags cannot hide failed room metrics."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit import audit_furnishing
from version import VERSION


class FurnishingAudit(unittest.TestCase):
    def setUp(self):
        self.room = dict(policy='zoned', densityAudited=True, accepted=True,
            warnings=[], connectedFloor=True, rect=[10, 20, 20, 20],
            floorSquares=400, furnishingSquares=200, occupiedSquares=60,
            targetDensity=[.18, .38], largestEmptySquare=dict(side=4),
            maxEmptySide=5, groups=[dict(footprint=60)])
        self.manifest = dict(version=VERSION,
            cells=[dict(records=[dict(furnishing=[self.room])])])

    def test_valid_metrics_pass_but_old_version_does_not(self):
        self.assertEqual(audit_furnishing(self.manifest),
                         ([self.room], [self.room]))
        self.manifest['version'] = 'old-version'
        with self.assertRaises(AssertionError):
            audit_furnishing(self.manifest)

    def test_absent_room_evidence_is_not_a_vacuous_pass(self):
        self.manifest['cells'][0]['records'][0]['furnishing'] = []
        with self.assertRaises(AssertionError):
            audit_furnishing(self.manifest)

    def test_boolean_pass_flags_cannot_be_truthy_strings(self):
        for key in ('densityAudited', 'accepted', 'connectedFloor'):
            with self.subTest(key=key):
                original = self.room[key]
                self.room[key] = 'false'
                with self.assertRaises(AssertionError):
                    audit_furnishing(self.manifest)
                self.room[key] = original

    def test_stale_pass_flag_cannot_hide_density_empty_patch_or_count_failure(self):
        for key, value in (('furnishingSquares', 100),
                           ('largestEmptySquare', dict(side=6)),
                           ('occupiedSquares', 59), ('floorSquares', 399)):
            with self.subTest(key=key):
                original = deepcopy(self.room[key])
                self.room[key] = value
                with self.assertRaises(AssertionError):
                    audit_furnishing(self.manifest)
                self.room[key] = original

    def test_compact_policy_remains_explicitly_not_density_certified(self):
        compact = dict(policy='compact', accepted=None, densityAudited=False,
                       reason='Fitted small-room recipe')
        self.manifest['cells'][0]['records'][0]['furnishing'].append(compact)
        audit_furnishing(self.manifest)
        compact['accepted'] = True
        with self.assertRaises(AssertionError):
            audit_furnishing(self.manifest)


if __name__ == '__main__':
    unittest.main()
