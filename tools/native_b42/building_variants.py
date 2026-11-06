"""100 distinct architectural variants per building category and kind (B42.21).

Each archetype has its own unmistakable exterior wall material family, window
and door frames, floor/roof surfaces, massing silhouettes, and compound/yard
features so players can identify building types at a glance.
"""

ARCHETYPE_KINDS = {
    'residential_country': ('cottage', 'house', 'ranch', 'duplex', 'rowhouse', 'farm'),
    'apartment_block': ('apartment', 'midrise', 'motel'),
    'highrise_tower': ('residentialtower', 'officetower', 'officeblock'),
    'commercial_retail': ('shop', 'generalstore', 'stripmall', 'diner', 'fuel', 'gas', 'laundry'),
    'gun_shop': ('gunshop',),
    'police_station': ('police',),
    'fire_station': ('firestation',),
    'military_camp': ('military', 'barracks', 'camp', 'checkpoint', 'gatehouse', 'guardhut', 'relay'),
    'shopping_mall': ('bigboxmall',),
    'medical_science': ('hospital', 'clinic', 'sanatorium', 'vet', 'lab'),
    'civic_education': ('school', 'kindergarten', 'civic', 'library', 'museum', 'archive', 'postoffice', 'chapel', 'gym', 'visitor'),
    'industrial_logistics': ('warehouse', 'workshop', 'garage', 'depot', 'terminal', 'waterworks', 'scrapyard', 'weighstation'),
}

KIND_ARCHETYPE = {k: arch for arch, kinds in ARCHETYPE_KINDS.items() for k in kinds}

WALL_PREFIXES = (
    'walls_exterior_house_', 'walls_commercial_', 'walls_exterior_wooden_',
    'walls_garage_', 'walls_interior_house_', 'walls_interior_bathroom_', 'walls_logs',
)

WALL_SETS = {
    'residential_country': (
        ('walls_exterior_house_01', 0), ('walls_exterior_house_01', 4),
        ('walls_exterior_house_01', 16), ('walls_exterior_house_01', 20),
        ('walls_exterior_house_02', 4), ('walls_exterior_house_02', 32),
        ('walls_exterior_house_02', 36), ('walls_exterior_house_02', 48),
        ('walls_exterior_wooden_01', 0), ('walls_exterior_wooden_01', 64),
        ('walls_logs', 0), ('walls_exterior_house_02', 52),
    ),
    'apartment_block': (
        ('walls_exterior_house_01', 32), ('walls_exterior_house_01', 48),
        ('walls_exterior_house_01', 52), ('walls_exterior_house_02', 16),
        ('walls_exterior_house_02', 32), ('walls_exterior_house_02', 36),
        ('walls_exterior_house_02', 48), ('walls_exterior_house_02', 64),
        ('walls_commercial_03', 0), ('walls_commercial_03', 16),
    ),
    'highrise_tower': (
        ('walls_commercial_03', 0), ('walls_commercial_03', 16),
        ('walls_commercial_03', 32), ('walls_commercial_03', 48),
        ('walls_commercial_01', 48), ('walls_exterior_house_02', 16),
        ('walls_exterior_house_02', 20), ('walls_exterior_house_02', 64),
    ),
    'commercial_retail': (
        ('walls_commercial_01', 48), ('walls_commercial_03', 0),
        ('walls_commercial_03', 16), ('walls_commercial_03', 32),
        ('walls_commercial_03', 48), ('walls_exterior_house_01', 16),
        ('walls_exterior_house_01', 20), ('walls_exterior_house_01', 32),
        ('walls_interior_bathroom_01', 0), ('walls_interior_bathroom_01', 16),
    ),
    'gun_shop': (
        ('walls_commercial_03', 16), ('walls_commercial_03', 32),
        ('walls_exterior_house_01', 48), ('walls_exterior_house_01', 52),
        ('walls_garage_01', 32), ('walls_garage_02', 16),
        ('walls_commercial_01', 48), ('walls_exterior_house_02', 64),
    ),
    'police_station': (
        ('walls_commercial_03', 0), ('walls_commercial_03', 32),
        ('walls_commercial_03', 48), ('walls_exterior_house_02', 16),
        ('walls_exterior_house_02', 64), ('walls_exterior_house_01', 32),
        ('walls_exterior_house_01', 48), ('walls_commercial_01', 48),
    ),
    'fire_station': (
        ('walls_exterior_house_01', 48), ('walls_exterior_house_01', 52),
        ('walls_commercial_03', 16), ('walls_garage_01', 32),
        ('walls_garage_02', 16), ('walls_exterior_house_01', 32),
        ('walls_exterior_house_02', 48), ('walls_exterior_house_02', 52),
    ),
    'military_camp': (
        ('walls_commercial_03', 32), ('walls_garage_01', 32),
        ('walls_garage_02', 16), ('walls_exterior_wooden_01', 0),
        ('walls_exterior_wooden_01', 64), ('walls_logs', 0),
        ('walls_exterior_house_02', 64), ('walls_commercial_03', 16),
    ),
    'shopping_mall': (
        ('walls_commercial_03', 0), ('walls_commercial_03', 16),
        ('walls_commercial_03', 32), ('walls_commercial_03', 48),
        ('walls_commercial_01', 48), ('walls_exterior_house_02', 16),
        ('walls_exterior_house_02', 48), ('walls_exterior_house_02', 64),
    ),
    'medical_science': (
        ('walls_exterior_house_02', 16), ('walls_exterior_house_02', 20),
        ('walls_exterior_house_02', 64), ('walls_commercial_03', 0),
        ('walls_commercial_03', 48), ('walls_interior_bathroom_01', 0),
        ('walls_interior_bathroom_01', 16), ('walls_interior_bathroom_01', 32),
    ),
    'civic_education': (
        ('walls_exterior_house_01', 0), ('walls_exterior_house_01', 16),
        ('walls_exterior_house_01', 32), ('walls_exterior_house_01', 48),
        ('walls_exterior_house_02', 16), ('walls_exterior_house_02', 32),
        ('walls_exterior_house_02', 48), ('walls_commercial_03', 0),
    ),
    'industrial_logistics': (
        ('walls_garage_01', 32), ('walls_garage_02', 16),
        ('walls_commercial_03', 16), ('walls_commercial_03', 32),
        ('walls_exterior_house_01', 48), ('walls_exterior_house_02', 64),
        ('walls_exterior_wooden_01', 0), ('walls_commercial_01', 48),
    ),
}

INTERIOR_WALL_SETS = (
    ('walls_interior_house_01', 0), ('walls_interior_house_01', 16),
    ('walls_interior_house_01', 32), ('walls_interior_house_01', 48),
    ('walls_interior_house_02', 0), ('walls_interior_house_02', 16),
    ('walls_interior_house_02', 32), ('walls_interior_house_02', 48),
    ('walls_interior_house_03', 0), ('walls_interior_house_03', 32),
    ('walls_interior_house_04', 0), ('walls_interior_house_04', 16),
    ('walls_interior_bathroom_01', 0), ('walls_interior_bathroom_01', 16),
)

WINDOW_SETS = {
    'residential_country': (('fixtures_windows_wood', 0), ('fixtures_windows_wood', 8), ('fixtures_windows_wood', 16), ('fixtures_windows_white', 0), ('fixtures_windows_white', 8), ('fixtures_windows_01', 0)),
    'apartment_block': (('fixtures_windows_white', 0), ('fixtures_windows_white', 8), ('fixtures_windows_white', 16), ('fixtures_windows_01', 0), ('fixtures_windows_01', 8), ('fixtures_windows_01', 24)),
    'highrise_tower': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_01', 16), ('fixtures_windows_01', 32), ('fixtures_windows_01', 56)),
    'commercial_retail': (('fixtures_windows_01', 0), ('fixtures_windows_01', 16), ('fixtures_windows_01', 32), ('fixtures_windows_metal', 0), ('fixtures_windows_white', 0)),
    'gun_shop': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_01', 32), ('fixtures_windows_01', 56)),
    'police_station': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_01', 16), ('fixtures_windows_white', 8)),
    'fire_station': (('fixtures_windows_metal', 0), ('fixtures_windows_white', 0), ('fixtures_windows_01', 0), ('fixtures_windows_01', 16)),
    'military_camp': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_wood', 0), ('fixtures_windows_01', 0)),
    'shopping_mall': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_01', 16), ('fixtures_windows_01', 32)),
    'medical_science': (('fixtures_windows_white', 0), ('fixtures_windows_white', 8), ('fixtures_windows_metal', 0), ('fixtures_windows_01', 16)),
    'civic_education': (('fixtures_windows_white', 0), ('fixtures_windows_white', 8), ('fixtures_windows_church', 0), ('fixtures_windows_church', 8), ('fixtures_windows_01', 0)),
    'industrial_logistics': (('fixtures_windows_metal', 0), ('fixtures_windows_metal', 8), ('fixtures_windows_01', 0), ('fixtures_windows_01', 32)),
}

INTERIOR_DOOR_SETS = (
    ('fixtures_doors_01', 0), ('fixtures_doors_01', 4), ('fixtures_doors_01', 8),
    ('fixtures_doors_01', 12), ('fixtures_doors_01', 16), ('fixtures_doors_01', 24),
    ('fixtures_doors_02', 0), ('fixtures_doors_02', 4), ('fixtures_doors_02', 12),
)

DOOR_SETS = {
    'residential_country': (('fixtures_doors_01', 0), ('fixtures_doors_01', 4), ('fixtures_doors_01', 8), ('fixtures_doors_01', 12), ('fixtures_doors_02', 0)),
    'apartment_block': (('fixtures_doors_01', 0), ('fixtures_doors_01', 16), ('fixtures_doors_01', 24), ('fixtures_doors_02', 4)),
    'highrise_tower': (('fixtures_doors_01', 24), ('fixtures_doors_01', 32), ('fixtures_doors_01', 56), ('fixtures_doors_02', 20)),
    'commercial_retail': (('fixtures_doors_01', 0), ('fixtures_doors_01', 24), ('fixtures_doors_01', 32), ('fixtures_doors_02', 12)),
    'gun_shop': (('fixtures_doors_01', 68), ('fixtures_doors_01', 56), ('fixtures_doors_01', 32)),
    'police_station': (('fixtures_doors_01', 68), ('fixtures_doors_01', 56), ('fixtures_doors_01', 32)),
    'fire_station': (('fixtures_doors_01', 32), ('fixtures_doors_01', 56), ('fixtures_doors_01', 0)),
    'military_camp': (('fixtures_doors_01', 68), ('fixtures_doors_01', 56), ('fixtures_doors_01', 32)),
    'shopping_mall': (('fixtures_doors_01', 24), ('fixtures_doors_01', 32), ('fixtures_doors_01', 0)),
    'medical_science': (('fixtures_doors_01', 24), ('fixtures_doors_01', 32), ('fixtures_doors_01', 68)),
    'civic_education': (('fixtures_doors_01', 0), ('fixtures_doors_01', 16), ('fixtures_doors_01', 24), ('fixtures_doors_02', 4)),
    'industrial_logistics': (('fixtures_doors_01', 56), ('fixtures_doors_01', 68), ('fixtures_doors_01', 32), ('fixtures_doors_01', 0)),
}

FLOOR_SETS = {
    'residential_country': (
        ('floors_interior_tilesandwood_01_40', 'floors_interior_tilesandwood_01_41', 'floors_interior_carpet_01_0', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_tilesandwood_01_42', 'floors_interior_tilesandwood_01_40', 'floors_interior_carpet_01_8', 'floors_interior_tilesandwood_01_17'),
        ('floors_interior_tilesandwood_01_44', 'floors_interior_carpet_01_12', 'floors_interior_tilesandwood_01_40', 'floors_interior_tilesandwood_01_18'),
        ('floors_interior_tilesandwood_01_46', 'floors_interior_tilesandwood_01_42', 'floors_interior_carpet_01_2', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_tilesandwood_01_41', 'floors_interior_tilesandwood_01_45', 'floors_interior_carpet_01_4', 'floors_interior_tilesandwood_01_19'),
        ('floors_interior_tilesandwood_01_43', 'floors_interior_tilesandwood_01_40', 'floors_interior_carpet_01_6', 'floors_interior_tilesandwood_01_20'),
        ('floors_interior_tilesandwood_01_45', 'floors_interior_tilesandwood_01_43', 'floors_interior_carpet_01_10', 'floors_interior_tilesandwood_01_21'),
        ('floors_interior_tilesandwood_01_47', 'floors_interior_tilesandwood_01_41', 'floors_interior_carpet_01_14', 'floors_interior_tilesandwood_01_22'),
        ('floors_interior_carpet_01_0', 'floors_interior_tilesandwood_01_40', 'floors_interior_carpet_01_9', 'floors_interior_tilesandwood_01_23'),
        ('floors_interior_carpet_01_3', 'floors_interior_tilesandwood_01_44', 'floors_interior_carpet_01_11', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_carpet_01_5', 'floors_interior_tilesandwood_01_46', 'floors_interior_carpet_01_13', 'floors_interior_tilesandwood_01_17'),
    ),
    'default': (
        ('floors_interior_tilesandwood_01_16', 'floors_interior_tilesandwood_01_40', 'floors_interior_carpet_01_0', 'floors_interior_tilesandwood_01_18'),
        ('floors_interior_tilesandwood_01_17', 'floors_interior_carpet_01_4', 'floors_interior_tilesandwood_01_42', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_tilesandwood_01_18', 'floors_interior_tilesandwood_01_20', 'floors_interior_carpet_01_10', 'floors_interior_tilesandwood_01_17'),
        ('floors_interior_tilesandwood_01_22', 'floors_interior_carpet_01_14', 'floors_interior_tilesandwood_01_44', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_tilesandwood_01_19', 'floors_interior_tilesandwood_01_41', 'floors_interior_carpet_01_1', 'floors_interior_tilesandwood_01_20'),
        ('floors_interior_tilesandwood_01_20', 'floors_interior_tilesandwood_01_43', 'floors_interior_carpet_01_2', 'floors_interior_tilesandwood_01_21'),
        ('floors_interior_tilesandwood_01_21', 'floors_interior_tilesandwood_01_45', 'floors_interior_carpet_01_3', 'floors_interior_tilesandwood_01_22'),
        ('floors_interior_tilesandwood_01_23', 'floors_interior_tilesandwood_01_47', 'floors_interior_carpet_01_5', 'floors_interior_tilesandwood_01_16'),
        ('floors_interior_carpet_01_6', 'floors_interior_tilesandwood_01_16', 'floors_interior_carpet_01_7', 'floors_interior_tilesandwood_01_18'),
        ('floors_interior_carpet_01_8', 'floors_interior_tilesandwood_01_17', 'floors_interior_carpet_01_9', 'floors_interior_tilesandwood_01_19'),
        ('floors_interior_carpet_01_11', 'floors_interior_tilesandwood_01_18', 'floors_interior_carpet_01_12', 'floors_interior_tilesandwood_01_20'),
    ),
}

ROOF_SETS = (
    'roofs_01_22', 'roofs_01_23', 'roofs_01_54', 'roofs_01_55',
    'roofs_02_22', 'roofs_02_54', 'roofs_03_22', 'roofs_03_54',
    'roofs_04_22', 'roofs_04_54', 'roofs_05_22', 'roofs_05_54', 'roofs_05_55',
)
SILHOUETTES = ('rect', 'courtyard_ne', 'courtyard_nw', 'u_court_north', 't_pavilion', 'stepped_podium', 'courtyard_ne_deep', 'courtyard_nw_deep', 'u_court_wide', 'stepped_twin')


def variant_spec(kind, seed=0):
    """Return deterministic variant 0..99 for `kind` with orthogonal visual/spatial traits."""
    vid = abs(int(seed)) % 100
    arch = KIND_ARCHETYPE.get(kind, 'commercial_retail')
    walls = WALL_SETS[arch]
    windows = WINDOW_SETS[arch]
    doors = DOOR_SETS[arch]
    floors = FLOOR_SETS.get(arch, FLOOR_SETS['default'])
    wall = walls[vid % len(walls)]
    upper_wall = walls[(vid * 3 + 1) % len(walls)]
    int_wall = INTERIOR_WALL_SETS[(vid // len(walls) + vid * 3) % len(INTERIOR_WALL_SETS)]
    win = windows[(vid // 2 + vid * 5) % len(windows)]
    ext_door = doors[(vid // 3 + vid * 7) % len(doors)]
    int_door = INTERIOR_DOOR_SETS[(vid * 9 + vid // 5) % len(INTERIOR_DOOR_SETS)] if arch not in ('gun_shop', 'police_station', 'military_camp') else ('fixtures_doors_01', (32, 56, 68)[vid % 3])
    fl_hall, fl_pri, fl_sec, fl_wet = floors[(vid + vid // len(walls)) % len(floors)]
    silhouette = SILHOUETTES[(vid // 10) % len(SILHOUETTES)]
    if kind == 'ranch':
        silhouette = 'courtyard_ne' if vid % 2 == 0 else 'courtyard_ne_deep'
    elif kind in ('guardhut', 'bigboxmall'):
        silhouette = 'rect'
    elif kind in ('garage', 'firestation', 'depot', 'stripmall') and silhouette in ('courtyard_nw', 'courtyard_nw_deep', 't_pavilion'):
        silhouette = 'courtyard_ne' if vid % 2 == 0 else 'stepped_podium'
    return dict(
        variant_id=vid,
        kind=kind,
        archetype=arch,
        silhouette=silhouette,
        spine_shift=(-1, 0, 1)[vid % 3],
        band_profile=(vid // 3) % 5,
        role_perm=(vid // 15) % 4,
        cut_depth=3 + (vid % 3),
        wall=wall,
        upper_wall=upper_wall,
        interior_wall=int_wall,
        window=win,
        window_period=3 + (vid % 3),
        window_mod=1 + (vid % 2),
        ext_door=ext_door,
        int_door=int_door,
        floors=dict(hall=fl_hall, primary=fl_pri, secondary=fl_sec, wet=fl_wet),
        roof=ROOF_SETS[vid % len(ROOF_SETS)],
        yard_style=vid % 10,
        sign_variant=vid % 12,
    )


def catalog_for_kind(kind):
    return [variant_spec(kind, i) for i in range(100)]


def catalog_for_archetype(archetype):
    kinds = ARCHETYPE_KINDS[archetype]
    return [variant_spec(kinds[i % len(kinds)], i) for i in range(100)]
