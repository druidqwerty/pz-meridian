"""Archetype-specific outdoor yards, compounds, fences, and forecourt props.

All compound elements are placed strictly outside room footprints (`owners`)
and at least one tile clear of exterior walls, doorways, and garage aprons.
"""

PAVING = 'floors_exterior_tilesandstone_01_0'
PLAZA = 'floors_exterior_tilesandstone_01_1'
LAWN = 'blends_natural_01_48'
GRAVEL = 'blends_street_01_86'

FENCES = {
    'picket': ('fencing_01_4', 'fencing_01_5'),
    'wood': ('fencing_01_20', 'fencing_01_21'),
    'chain': ('fencing_01_16', 'fencing_01_17'),
    'high_chain': ('fencing_01_72', 'fencing_01_73'),
    'security': ('fencing_01_112', 'fencing_01_113'),
    'sandbag': ('carpentry_02_12', 'carpentry_02_13'),
}

FLOWERS = ('vegetation_ornamental_01_16', 'vegetation_ornamental_01_17',
           'vegetation_ornamental_01_18', 'vegetation_ornamental_01_19')
HEDGES = ('vegetation_ornamental_01_0', 'vegetation_ornamental_01_1')
TREES = ('vegetation_trees_01_8', 'vegetation_trees_01_9', 'vegetation_trees_01_13')
PATIO_CHAIRS = ('furniture_seating_outdoor_01_16', 'furniture_seating_outdoor_01_17',
                'furniture_seating_outdoor_01_18', 'furniture_seating_outdoor_01_19')
MAILBOXES = ('street_decoration_01_18', 'street_decoration_01_19',
             'street_decoration_01_20', 'street_decoration_01_21')
MIL_CRATES = ('location_military_generic_01_0', 'location_military_generic_01_1',
              'location_military_generic_01_14', 'location_military_generic_01_15')


def dress_building_exterior(tiles, x, y, w, h, kind, spec, owners_z0):
    """Populate outdoor courtyard cutouts and archetype forecourt markers."""
    arch = spec['archetype']
    vid = spec['variant_id']
    # Find all cutout squares inside the (w, h) bounding box on z=0 that are
    # outside `owners_z0` and do not host the east/south exterior wall of a room.
    court = sorted(
        (dx, dy) for dx in range(w) for dy in range(h - 2)
        if (dx, dy) not in owners_z0
        and (dx - 1, dy) not in owners_z0
        and (dx, dy - 1) not in owners_z0
    )
    if court:
        _dress_courtyard(tiles, x, y, w, h, arch, vid, court)
    _dress_forecourt(tiles, x, y, w, h, kind, arch, vid)


def _dress_courtyard(tiles, x, y, w, h, arch, vid, court):
    court_set = set(court)
    if arch == 'residential_country':
        ground = LAWN if vid % 3 != 0 else PLAZA
        fence_w, fence_n = FENCES['picket' if vid % 2 == 0 else 'wood']
        props = (FLOWERS[vid % 4], PATIO_CHAIRS[vid % 4], TREES[vid % 3])
    elif arch in ('gun_shop', 'military_camp'):
        ground = GRAVEL if vid % 2 == 0 else PAVING
        fence_w, fence_n = FENCES['high_chain' if vid % 2 == 0 else 'security']
        props = (MIL_CRATES[vid % 4], 'carpentry_02_13', 'location_military_generic_01_21')
    elif arch == 'police_station':
        ground = PAVING
        fence_w, fence_n = FENCES['high_chain']
        props = ('street_decoration_01_26', 'lighting_outdoor_01_0', 'location_military_generic_01_18')
    elif arch == 'fire_station':
        ground = PAVING
        fence_w, fence_n = FENCES['chain']
        props = ('street_decoration_01_12', 'street_decoration_01_26', 'lighting_outdoor_01_0')
    elif arch in ('industrial_logistics',):
        ground = GRAVEL if vid % 2 == 0 else PAVING
        fence_w, fence_n = FENCES['chain' if vid % 2 == 0 else 'high_chain']
        props = ('carpentry_02_104', 'location_military_generic_01_14', 'trashcontainers_01_0')
    else:
        ground = PLAZA if vid % 2 == 0 else LAWN
        fence_w, fence_n = FENCES['picket' if arch == 'civic_education' else 'chain']
        props = (FLOWERS[vid % 4], PATIO_CHAIRS[vid % 4], 'vegetation_indoor_01_8')

    for dx, dy in court:
        tiles[x + dx, y + dy, 0] = [ground]
        if dy == 0 and dx % 3 != 1:
            tiles[x + dx, y + dy, 0].append(fence_n)
        elif dx == 0 and dy % 3 != 1:
            tiles[x + dx, y + dy, 0].append(fence_w)

    inner = [(dx, dy) for dx, dy in court
             if (dx - 1, dy) in court_set and (dx + 1, dy) in court_set
             and (dx, dy - 1) in court_set and (dx, dy + 1) in court_set]
    for idx, (dx, dy) in enumerate(inner[::max(1, len(inner) // 3 or 1)][:3]):
        sprite = props[idx % len(props)]
        if sprite not in tiles[x + dx, y + dy, 0]:
            tiles[x + dx, y + dy, 0].append(sprite)


def _dress_forecourt(tiles, x, y, w, h, kind, arch, vid):
    """Place non-blocking archetype markers along the front corner apron."""
    if y + h + 2 >= 255 or x + w - 2 >= 255:
        return
    corner_w = (x + 1, y + h + 1, 0)
    corner_e = (x + w - 2, y + h + 1, 0)
    if arch == 'residential_country':
        tiles[corner_w] = [LAWN, MAILBOXES[vid % 4]]
        tiles[corner_e] = [LAWN, FLOWERS[vid % 4]]
    elif arch == 'fire_station':
        tiles[corner_e] = [PAVING, 'street_decoration_01_12']
        tiles[corner_w] = [PAVING, 'street_decoration_01_26']
    elif arch == 'police_station':
        tiles[corner_w] = [PAVING, 'street_decoration_01_26']
        tiles[corner_e] = [PAVING, 'lighting_outdoor_01_0']
    elif arch in ('gun_shop', 'military_camp'):
        tiles[corner_w] = [PAVING, 'carpentry_02_13']
        tiles[corner_e] = [PAVING, 'location_military_generic_01_21' if vid % 2 == 0 else 'location_military_generic_01_18']
    elif arch == 'commercial_retail' and kind not in ('fuel', 'gas'):
        tiles[corner_w] = [PLAZA, PATIO_CHAIRS[vid % 4] if kind == 'diner' else 'vegetation_indoor_01_8']
        tiles[corner_e] = [PLAZA, 'trashcontainers_01_20']
    elif arch in ('highrise_tower', 'apartment_block', 'civic_education', 'medical_science'):
        tiles[corner_w] = [PLAZA, 'vegetation_indoor_01_8']
        tiles[corner_e] = [PLAZA, FLOWERS[vid % 4]]
