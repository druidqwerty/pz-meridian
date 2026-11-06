"""Complete, purpose-specific native facade lettering, never loose grid parts."""

WALL_PREFIXES = (
    'walls_exterior_house_', 'walls_commercial_', 'walls_exterior_wooden_',
    'walls_garage_', 'walls_interior_house_', 'walls_interior_bathroom_', 'walls_logs_',
)


def row(sheet, start, length):
    return tuple((i, 0, sheet+str(start+i)) for i in range(length))


SIGNS = {
    'police': row('location_community_police_01_', 16, 3),
    'firestation': row('location_community_medical_01_', 92, 4),
    'clinic': ((0, 0, 'location_community_medical_01_55'),),
    'hospital': row('location_community_medical_01_', 92, 4),
    'sanatorium': row('location_community_medical_01_', 80, 2),
    'vet': row('signs_one-off_01_', 40, 4),
    'school': row('location_shop_accessories_genericsigns_01_', 16, 4),
    'kindergarten': row('signs_one-off_09_', 80, 4),
    'shop': row('location_shop_zippee_01_', 43, 3),
    'generalstore': row('location_shop_greenes_01_', 48, 3),
    'stripmall': row('location_shop_accessories_genericsigns_01_', 24, 4),
    'bigboxmall': ((0, 0, 'advertising_02_1'),),
    'gunshop': row('signs_one-off_01_', 52, 4),
    'fuel': row('location_shop_fossoil_01_', 29, 3),
    'gas': row('location_shop_fossoil_01_', 29, 3),
    'diner': row('location_restaurant_diner_01_', 52, 4),
    'motel': row('location_hospitality_sunstarmotel_02_', 2, 4),
    'laundry': row('appliances_laundry_01_', 16, 3),
    'library': row('signs_miscbrands_01_', 16, 4),
    'archive': row('signs_miscbrands_01_', 16, 4),
    'museum': row('signs_one-off_09_', 60, 4),
    'civic': row('signs_one-off_09_', 84, 4),
    'gym': row('signs_one-off_09_', 84, 4),
    'visitor': row('location_shop_accessories_genericsigns_01_', 20, 2),
    'chapel': row('location_community_police_01_', 78, 2),
    'postoffice': row('location_shop_accessories_genericsigns_01_', 43, 3),
    'officeblock': row('location_shop_accessories_genericsigns_01_', 43, 3),
    'officetower': row('location_shop_accessories_genericsigns_01_', 43, 3),
    'garage': row('signs_one-off_01_', 67, 4),
    'workshop': row('construction_01_', 56, 4),
    'depot': row('construction_01_', 56, 4),
    'warehouse': row('construction_01_', 56, 4),
    'scrapyard': row('signs_one-off_01_', 67, 4),
    'military': row('location_military_generic_01_', 16, 2),
    'barracks': row('location_military_generic_01_', 16, 2),
    'camp': row('location_military_generic_01_', 16, 2),
    'checkpoint': row('location_military_generic_01_', 19, 2),
    'gatehouse': row('location_military_generic_01_', 19, 2),
    'bunker': row('location_military_generic_01_', 19, 2),
    'lab': row('location_military_generic_01_', 19, 2),
    'guardhut': ((0, 0, 'location_military_generic_01_21'),),
}

SIGN_VARIANTS = {
    'shop': (
        row('location_shop_zippee_01_', 43, 3),
        row('location_shop_bargNclothes_01_', 16, 4),
        row('location_shop_accessories_genericsigns_01_', 59, 3),
        row('location_shop_accessories_genericsigns_01_', 76, 4),
        row('location_shop_mall_signs_01_', 108, 4),
        row('signs_miscbrands_01_', 24, 4),
        row('signs_one-off_09_', 60, 4),
    ),
    'generalstore': (
        row('location_shop_greenes_01_', 48, 3),
        row('location_shop_zippee_01_', 43, 3),
        row('location_shop_mall_signs_01_', 60, 4),
        row('location_shop_accessories_genericsigns_01_', 59, 3),
    ),
    'stripmall': (
        row('location_shop_accessories_genericsigns_01_', 24, 4),
        row('location_shop_bargNclothes_01_', 16, 4),
        row('location_shop_mall_signs_01_', 132, 4),
        row('location_shop_mall_signs_01_', 76, 4),
        row('location_shop_accessories_genericsigns_01_', 0, 3),
    ),
    'diner': (
        row('location_restaurant_diner_01_', 52, 4),
        row('location_restaurant_seahorse_01_', 64, 3),
        row('location_restaurant_spiffos_02_', 46, 2),
        row('location_shop_mall_signs_01_', 12, 4),
        row('location_shop_mall_signs_01_', 20, 4),
        row('signs_miscbrands_01_', 40, 4),
    ),
    'gunshop': (
        row('signs_one-off_01_', 52, 4),
        row('location_military_generic_01_', 16, 2),
        row('location_military_generic_01_', 19, 2),
    ),
    'clinic': (
        ((0, 0, 'location_community_medical_01_55'),),
        row('location_community_medical_01_', 80, 2),
        row('location_shop_mall_signs_01_', 108, 4),
    ),
}


def _supports_sign(names):
    for n in names:
        if not n.startswith(WALL_PREFIXES):
            continue
        idx = int(n.rsplit('_', 1)[1])
        if n.startswith('walls_garage_01_') and idx < 16:
            continue
        if idx % 16 in (1, 5, 9, 13):
            return True
    return False


def place_building_sign(tiles, rect, kind, z=0, variant=None):
    """Mount complete south-facing signage on a supported south facade."""
    group = SIGNS.get(kind)
    if not group:
        return []
    if variant is not None and kind in SIGN_VARIANTS:
        options = SIGN_VARIANTS[kind]
        group = options[int(variant) % len(options)]
    x, y, w, h = rect
    width = 1 + max(dx for dx, _, _ in group)
    yy = y + h
    for sx in range(x + 1, x + w - width):
        positions = [(sx + dx, yy + dy, sprite) for dx, dy, sprite in group]
        if not all(0 <= xx < 256 and 0 <= yyy < 256 and
                   _supports_sign(tiles.get((xx, yyy, z), ()))
                   for xx, yyy, _ in positions):
            continue
        result = []
        for xx, yyy, sprite in positions:
            names = tiles.setdefault((xx, yyy, z), [])
            if sprite not in names:
                names.append(sprite)
            result.append(dict(x=xx, y=yyy, z=z, sprite=sprite, kind=kind))
        return result
    return []
