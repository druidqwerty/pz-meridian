"""Curated B42.21 facing tables verified in newtiledefinitions.tiles.txt.

Facing is the visible/use front, not the supporting wall. North-wall furniture
faces S; west-wall furniture faces E. Never rotate by numeric-ID arithmetic.
Only single-square sprites belong here; beds/sofas use explicit grid groups.
"""


def family(sheet, ids):
    return {d: sheet + str(n) for d, n in zip('NESW', ids)}


FACING = {
    'fridge': family('appliances_refrigeration_01_', (2, 1, 0, 3)),
    'oven': family('appliances_cooking_01_', (3, 0, 1, 2)),
    'counter': family('fixtures_counters_01_', (1, 3, 5, 7)),
    'sink': family('fixtures_sinks_01_', (0, 1, 2, 3)),
    'toilet': family('fixtures_bathroom_01_', (7, 5, 4, 6)),
    'dresser': family('furniture_storage_01_', (11, 8, 9, 10)),
    'shelves': family('furniture_shelving_01_', (43, 41, 40, 42)),
    'metal': family('furniture_storage_02_', (2, 1, 0, 3)),
    'desk': family('location_community_school_01_', (6, 4, 5, 7)),
    'chair': family('furniture_seating_indoor_02_', (7, 4, 5, 6)),
    'armchair': family('furniture_seating_indoor_01_', (11, 8, 9, 10)),
    'lamp': family('lighting_indoor_02_', (0, 1, 2, 3)),
}

# SpriteGridPos is (x,y), rather than draw order or head/foot guessed from ID.
BED_GROUPS = {
    'S': ((0, 0, 'furniture_bedding_01_9'), (0, 1, 'furniture_bedding_01_8')),
    'E': ((0, 0, 'furniture_bedding_01_10'), (1, 0, 'furniture_bedding_01_11')),
}
SOFA_GROUPS = {
    'S': ((0, 0, 'furniture_seating_indoor_01_0'), (1, 0, 'furniture_seating_indoor_01_1')),
    'N': ((0, 0, 'furniture_seating_indoor_01_6'), (1, 0, 'furniture_seating_indoor_01_7')),
    'E': ((0, 0, 'furniture_seating_indoor_01_3'), (0, 1, 'furniture_seating_indoor_01_2')),
    'W': ((0, 0, 'furniture_seating_indoor_01_5'), (0, 1, 'furniture_seating_indoor_01_4')),
}
MEDICAL_GROUP = ((0, 0, 'location_community_medical_01_17'),
                 (0, 1, 'location_community_medical_01_16'))


def facing(key, direction='S', base=None):
    if key in FACING:
        return FACING[key][direction]
    return base[key]


ALL_SPRITES = {s for fs in FACING.values() for s in fs.values()}
ALL_SPRITES.update(s for groups in (BED_GROUPS, SOFA_GROUPS)
                   for group in groups.values() for _, _, s in group)
ALL_SPRITES.update(s for _, _, s in MEDICAL_GROUP)
