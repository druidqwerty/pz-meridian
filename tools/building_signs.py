"""Complete, purpose-specific native facade lettering, never loose grid parts."""


def row(sheet, start, length):
    return tuple((i, 0, sheet+str(start+i)) for i in range(length))


SIGNS = {
    'police': row('location_community_police_01_', 16, 3),
    'clinic': ((0, 0, 'location_community_medical_01_55'),),
    'hospital': row('location_community_medical_01_', 92, 4),
    'school': row('location_shop_accessories_genericsigns_01_', 16, 4),
    'shop': row('location_shop_zippee_01_', 43, 3),
    'generalstore': row('location_shop_zippee_01_', 43, 3),
    'stripmall': row('location_shop_accessories_genericsigns_01_', 24, 4),
    'bigboxmall': ((0, 0, 'advertising_02_1'),),
    'gunshop': row('signs_one-off_01_', 52, 4),
    'fuel': row('location_shop_fossoil_01_', 29, 3),
    'gas': row('location_shop_fossoil_01_', 29, 3),
    'diner': row('location_restaurant_diner_01_', 52, 4),
    'laundry': row('appliances_laundry_01_', 16, 3),
    'library': row('signs_miscbrands_01_', 16, 4),
    'military': row('location_military_generic_01_', 16, 2),
    'barracks': row('location_military_generic_01_', 16, 2),
    'checkpoint': row('location_military_generic_01_', 19, 2),
    'gatehouse': row('location_military_generic_01_', 19, 2),
    'bunker': row('location_military_generic_01_', 19, 2),
    'lab': row('location_military_generic_01_', 19, 2),
    'guardhut': ((0, 0, 'location_military_generic_01_21'),),
}


def place_building_sign(tiles, rect, kind, z=0):
    """Mount complete south-facing signage on a supported south facade.

    Rect and returned coordinates are CELL-local. No floor, doorway or room
    object is replaced. Native signs can span window wall sections above glass.
    """
    group = SIGNS.get(kind)
    if not group:
        return []
    x, y, w, h = rect
    width = 1+max(dx for dx, _, _ in group)
    yy = y+h
    for sx in range(x+1, x+w-width):
        positions = [(sx+dx, yy+dy, sprite) for dx, dy, sprite in group]
        if not all(0 <= xx < 256 and 0 <= yyy < 256 and
                   any(n.startswith('walls_exterior_house_02_') and
                       int(n.rsplit('_',1)[1])%16 in (1,9)
                       for n in tiles.get((xx,yyy,z),()))
                   for xx, yyy, _ in positions):
            continue
        result = []
        for xx, yyy, sprite in positions:
            names = tiles.setdefault((xx,yyy,z),[])
            if sprite not in names:
                names.append(sprite)
            result.append(dict(x=xx,y=yyy,z=z,sprite=sprite,kind=kind))
        return result
    return []
