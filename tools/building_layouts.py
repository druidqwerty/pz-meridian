"""Original, function-specific floor plans with 100 variant geometries per kind.

The circulation room is always first. Its southern landing preserves the native
three-tile westward stair flight. Other rooms carry a separate furnishing theme.
No exterior picture or third-party floor plan is imported into the product.
"""
from building_variants import variant_spec

DOMESTIC = {'house', 'cottage', 'ranch', 'duplex', 'rowhouse', 'farm', 'camp'}
TOWERS = {'midrise', 'officeblock', 'residentialtower', 'officetower', 'apartment'}
SERVICE = {'garage', 'workshop', 'depot', 'warehouse', 'scrapyard', 'waterworks',
           'firestation', 'terminal', 'gym', 'chapel'}

PAIR_WEIGHTS = ((5, 7), (6, 6), (7, 5), (5, 6), (6, 5))
TRIPLE_WEIGHTS = ((5, 5, 3), (6, 5, 3), (5, 6, 3), (6, 6, 3), (7, 5, 3))
QUAD_WEIGHTS = ((5, 6, 6, 3), (5, 7, 6, 3), (4, 6, 7, 3), (6, 6, 6, 3), (4, 7, 6, 3))


def segments(length, weights):
    """Integer contiguous bands, with no zero-width or uncovered seam."""
    cuts = [0]
    total = sum(weights)
    for i in range(1, len(weights)):
        cuts.append(round(length * sum(weights[:i]) / total))
    cuts.append(length)
    return list(zip(cuts[:-1], cuts[1:]))


def _w2(vid):
    return list(PAIR_WEIGHTS[vid % len(PAIR_WEIGHTS)])


def _w3(vid):
    return list(TRIPLE_WEIGHTS[vid % len(TRIPLE_WEIGHTS)])


def _w4(vid):
    return list(QUAD_WEIGHTS[vid % len(QUAD_WEIGHTS)])


def _wing_cut(spec, top, n_rooms, z, side):
    """Safe courtyard or upper-floor setback cutout that keeps rooms >= 4 deep."""
    max_cut = max(0, top - max(12, n_rooms * 5))
    if max_cut < 3:
        return 0
    sil = spec['silhouette']
    want = min(spec['cut_depth'], max_cut)
    if sil in ('courtyard_ne', 'courtyard_ne_deep') and side == 'E':
        return want
    if sil in ('courtyard_nw', 'courtyard_nw_deep') and side == 'W':
        return want
    if sil == 't_pavilion':
        return min(3, max_cut)
    if sil in ('stepped_podium', 'stepped_twin') and z > 0 and side == ('E' if (spec['variant_id'] + z) % 2 == 0 else 'W'):
        return want
    return 0


def layout(w, h, roles, kind, seed=0, z=0, levels=1):
    spec = variant_spec(kind, seed)
    vid = spec['variant_id']
    landing = 4 if levels > 1 else 2
    top = h - landing
    hallw = 3 if levels > 1 or w >= 24 else 2
    mid = (w - hallw) // 2
    if w >= 28 and kind not in ('bigboxmall', 'guardhut', 'ranch') and kind not in SERVICE:
        shift = spec['spine_shift']
        if mid + shift >= 11 and (w - (mid + shift) - hallw) >= 11:
            mid += shift
    hall_y = 2 if (spec['silhouette'] in ('u_court_north', 'u_court_wide') and top >= 16 and kind not in ('guardhut', 'bigboxmall', 'ranch')) else 0
    hall = [(mid, hall_y, hallw, top - hall_y), (0, top, w, landing)]
    rooms = [dict(name='hall', rects=hall, theme='hall')]

    def add(name, rect, theme=None):
        a, b, c, d = rect
        if c < 3 or d < 3:
            raise ValueError((kind, 'Room too narrow', rect))
        rooms.append(dict(name=name, rects=[rect], theme=theme or name))

    def bands(x, width, names, start=0, end=None, themes=None, weights=None):
        end = top if end is None else end
        for i, (a, b) in enumerate(segments(end - start, weights or [1] * len(names))):
            add(names[i], (x, start + a, width, b - a), themes[i] if themes else None)

    if kind == 'bigboxmall':
        from mall_layout import mall_rooms
        rooms = mall_rooms(w, h, landing)
    elif kind == 'gunshop':
        ce = _wing_cut(spec, top, 3, z, 'E')
        add('gunstore', (0, 0, mid, top), 'gunstore')
        e_names = ['gunstorestorage', 'office', 'bathroom'] if vid % 2 == 0 else ['office', 'gunstorestorage', 'bathroom']
        e_themes = ['storage', 'office', 'bathroom'] if vid % 2 == 0 else ['office', 'storage', 'bathroom']
        bands(mid + hallw, w - mid - hallw, e_names, start=ce, weights=_w3(vid), themes=e_themes)
    elif kind == 'guardhut':
        rooms[0]['rects'] = [(0, top, w, landing)]
        add('office', (0, 0, w, top), 'communications')
    elif kind in SERVICE:
        spine = max(8, w - 11)
        hall[0] = (spine, 0, 3, top)
        add('hall' if kind in ('gym', 'chapel', 'terminal') else 'storage',
            (0, 0, spine, top),
            'gym' if kind == 'gym' else 'assembly' if kind in ('chapel', 'terminal') else
            'pump' if kind == 'waterworks' else 'workshop' if kind != 'warehouse' else 'storage')
        ce = _wing_cut(spec, top, 3 if top >= 14 else 2, z, 'E')
        if top - ce >= 12:
            e_names = ['office', 'storage', 'bathroom'] if vid % 2 == 0 else ['storage', 'office', 'bathroom']
            bands(spine + 3, w - spine - 3, e_names, start=ce, weights=_w3(vid))
        else:
            bands(spine + 3, w - spine - 3, ['office', 'bathroom'], start=ce, weights=_w2(vid))
    elif kind == 'ranch':
        mid = 10 + (-1 if vid % 3 == 1 else 0)
        hall[0] = (mid, 0, 2, top)
        bands(0, mid, ['kitchen', 'livingroom'], weights=[5, 7])
        bands(mid + 2, w - mid - 2, ['bedroom', 'bathroom'], start=5 + (vid % 2), weights=[6, 4])
    elif kind in DOMESTIC:
        if kind == 'duplex':
            cw = _wing_cut(spec, top, 4, z, 'W')
            ce = _wing_cut(spec, top, 4, z, 'E')
            for a, width, cut in ((0, mid, cw), (mid + hallw, w - mid - hallw, ce)):
                bands(a, width, ['kitchen', 'bedroom', 'livingroom', 'bathroom'], start=cut, weights=[5, 6, 6, 3])
        elif kind == 'rowhouse':
            ce = _wing_cut(spec, top, 2, z, 'E')
            bands(0, mid, ['kitchen', 'livingroom'] if z == 0 else ['bedroom', 'bedroom'], weights=[5, 7])
            bands(mid + hallw, w - mid - hallw, ['livingroom', 'bathroom'] if z == 0 else ['bedroom', 'bathroom'],
                  start=ce, weights=[7, 4])
        else:
            cw = _wing_cut(spec, top, 2, z, 'W')
            ce = _wing_cut(spec, top, 2, z, 'E')
            bands(0, mid, ['kitchen', 'livingroom'], start=cw, weights=[5, 6])
            bands(mid + hallw, w - mid - hallw, ['bedroom', 'bathroom'], start=ce, weights=[7, 4])
    elif kind in TOWERS:
        office = kind in ('officeblock', 'officetower')
        cw = _wing_cut(spec, top, 4 if z > 0 else 3, z, 'W')
        ce = _wing_cut(spec, top, 4 if z > 0 else 3, z, 'E')
        if z == 0:
            bands(0, mid, ['office', 'grocery', 'storage'], start=cw, weights=_w3(vid))
            bands(mid + hallw, w - mid - hallw, ['office', 'hall', 'bathroom'], start=ce,
                  weights=_w3(vid + 1), themes=['office', 'assembly', 'bathroom'])
        elif office:
            bands(0, mid, ['office', 'office', 'office', 'office'], start=cw, weights=_w4(vid))
            bands(mid + hallw, w - mid - hallw, ['office', 'office', 'storage', 'bathroom'], start=ce, weights=_w4(vid + 2))
        else:
            for a, width, cut in ((0, mid, cw), (mid + hallw, w - mid - hallw, ce)):
                bands(a, width, ['kitchen', 'bedroom', 'livingroom', 'bathroom'], start=cut, weights=[5, 7, 7, 3])
    elif kind in ('school', 'kindergarten'):
        ce = _wing_cut(spec, top, 3, z, 'E')
        bands(0, mid, ['classroom'] * 3 if kind == 'school' else ['classroom', 'livingroom'],
              themes=['classroom'] * 3 if kind == 'school' else ['nursery', 'livingroom'],
              weights=_w3(vid) if kind == 'school' else _w2(vid))
        bands(mid + hallw, w - mid - hallw, ['library', 'office', 'bathroom'], start=ce, weights=_w3(vid + 1))
    elif kind in ('police', 'checkpoint', 'gatehouse', 'military', 'barracks'):
        cw = _wing_cut(spec, top, 2, z, 'W')
        ce = _wing_cut(spec, top, 3, z, 'E')
        store = 'policestorage' if kind == 'police' else 'armystorage'
        w_names = [store, 'office'] if vid % 2 == 0 else ['office', store]
        bands(0, mid, w_names, start=cw, weights=_w2(vid))
        bands(mid + hallw, w - mid - hallw, ['office', 'bedroom', 'bathroom'], start=ce,
              weights=_w3(vid), themes=['communications', 'bedroom', 'bathroom'])
    elif kind in ('shop', 'generalstore', 'stripmall', 'fuel', 'gas', 'diner', 'motel'):
        ce = _wing_cut(spec, top, 3 if kind in ('stripmall', 'motel') else 2, z, 'E')
        if kind == 'stripmall':
            bands(0, mid, ['grocery', 'grocery', 'grocery'], weights=_w3(vid))
            bands(mid + hallw, w - mid - hallw, ['storage', 'office', 'bathroom'], start=ce, weights=_w3(vid + 1))
        elif kind == 'motel':
            cw = _wing_cut(spec, top, 3, z, 'W')
            bands(0, mid, ['bedroom', 'bedroom', 'bedroom'], start=cw, weights=_w3(vid))
            bands(mid + hallw, w - mid - hallw, ['bedroom', 'bedroom', 'bathroom'], start=ce, weights=_w3(vid + 2))
        else:
            cw = _wing_cut(spec, top, 1, z, 'W')
            add('kitchen' if kind == 'diner' else 'gasstore' if kind in ('fuel', 'gas') else 'grocery',
                (0, cw, mid, top - cw))
            bands(mid + hallw, w - mid - hallw,
                  ['livingroom', 'bathroom'] if kind == 'diner' else ['storage', 'bathroom'],
                  start=ce, themes=['assembly', 'bathroom'] if kind == 'diner' else None, weights=[7, 3])
    elif kind in ('hospital', 'clinic', 'sanatorium', 'vet', 'lab'):
        cw = _wing_cut(spec, top, 3, z, 'W')
        ce = _wing_cut(spec, top, 3, z, 'E')
        bands(0, mid, ['laboratory', 'laboratory', 'medicalstorage'] if kind == 'lab' else
              ['hospitalroom', 'medical', 'medicalstorage'], start=cw, weights=_w3(vid))
        bands(mid + hallw, w - mid - hallw, ['office', 'medical', 'bathroom'], start=ce, weights=_w3(vid + 1))
    else:
        cw = _wing_cut(spec, top, 2, z, 'W')
        ce = _wing_cut(spec, top, 2, z, 'E')
        names = list(roles)
        bands(0, mid, names[:2], start=cw, weights=[6, 5] if vid % 2 == 0 else [5, 6])
        bands(mid + hallw, w - mid - hallw, names[2:], start=ce, weights=[7, 3])

    owners = {}
    for i, room in enumerate(rooms):
        for a, b, c, d in room['rects']:
            for xx in range(a, a + c):
                for yy in range(b, b + d):
                    if (xx, yy) in owners:
                        raise ValueError((kind, 'overlapping rooms', xx, yy))
                    owners[xx, yy] = i
    doors = set()
    for i in range(1, len(rooms)):
        candidates = []
        for (xx, yy), owner in owners.items():
            if owner != i:
                continue
            for dx, dy, direction in ((-1, 0, 'W'), (1, 0, 'W'), (0, -1, 'N'), (0, 1, 'N')):
                if owners.get((xx + dx, yy + dy)) == 0:
                    candidates.append((max(xx, xx + dx), max(yy, yy + dy), direction))
        if not candidates:
            raise ValueError((kind, 'room does not reach circulation', i))
        doors.add(candidates[len(candidates) // 2])
    return rooms, doors, owners
