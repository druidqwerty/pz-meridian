"""Native entrance-pavilion wayfinding/content; no gameplay or custom assets.

Integrate AFTER build_bunker. Native stairs, ceiling holes, doors and corridors
are never moved. All reported points are absolute world coordinates.
"""
from collections import defaultdict
from furnishing import furnish_room

FLOORS = {'floors_interior_tilesandwood_01_' + str(n) for n in (16, 18, 20, 22, 24, 40, 48)}
ACCENT = 'floors_interior_tilesandwood_01_24'
LIGHT_ACCENT = 'floors_interior_tilesandwood_01_18'
EXIT = {'N': 'lighting_indoor_01_25', 'W': 'lighting_indoor_01_24'}
PROGRAM = {
    'medical': ('medical', 'waitingroom'), 'staff': ('office', 'storage'),
    'research': ('communications', 'storage'), 'isolation': ('medical', 'storage'),
    'public': ('office', 'waitingroom'), 'water': ('workshop', 'storage'),
    'cargo': ('storage', 'office'), 'power': ('electrical', 'storage'),
    'maintenance': ('workshop', 'storage'), 'records': ('archive', 'office'),
    'command': ('communications', 'office'), 'emergency': ('waitingroom', 'storage'),
}


def _solid_wall(names, direction):
    offset = 1 if direction == 'N' else 0
    return any(n.startswith('walls_exterior_house_02_') and
               int(n.rsplit('_', 1)[1]) % 16 == offset for n in names)


def decorate(tiles, cx, cy, bunker):
    """Return original native signs, changed-floor and furniture coordinates.

    Call once after bunker geometry; repeat calls are idempotent. Furniture bays
    are two narrow side alcoves, never the stair/door axis or the two lower flights.
    The EXIT text belongs to a vanilla sign, not invented labels on a tile.
    """
    result = dict(signs=[], floorTrail=[], props=[], movedWallCabinets=[])
    for entrance in bunker.get('entrances', []):
        if entrance['x'] // 256 != cx or entrance['y'] // 256 != cy:
            continue
        role = entrance.get('role', 'research')
        accent = LIGHT_ACCENT if bunker.get('wing', {}).get('floor') == ACCENT else ACCENT
        world = lambda x, y, z: dict(x=cx*256+x, y=cy*256+y, z=z)
        # Two-tile strip to the WEST upper landing, never across the open shaft.
        route = {(x, y) for x in (130, 131) for y in range(132, 144)}
        route |= {(x, y) for x in range(126, 132) for y in (132, 133)}
        route |= {(x, y) for x in (126, 127) for y in range(128, 134)}
        for x, y in sorted(route):
            names = tiles.get((x, y, 0), [])
            if any(n.startswith('fixtures_stairs_01_') for n in names):
                continue
            # Only the existing walkable finish changes. No square/floor is added.
            for i, sprite in enumerate(names):
                if sprite in FLOORS:
                    names[i] = accent
                    result['floorTrail'].append(world(x, y, 0))
                    break
        # Native E/S-facing EXIT signs require a matching W/N solid wall.
        # They identify the surface-return zone, not a fictional directional arrow.
        for x, y, z, direction in ((125, 120, 0, 'N'), (121, 120, -1, 'N')):
            names = tiles.get((x, y, z), [])
            if not _solid_wall(names, direction):
                continue
            sprite = EXIT[direction]
            if sprite not in names:
                names.append(sprite)
            result['signs'].append(world(x, y, z) | dict(sprite=sprite))
        # The legacy medicine cabinet was a wall object standing in open space.
        # Relocate only that exact sprite to an intact, north-backed wall.
        medicine = 'fixtures_bathroom_01_28'
        old = tiles.get((123, 122, 0), [])
        target = tiles.get((124, 120, 0), [])
        if medicine in old and _solid_wall(target, 'N'):
            old.remove(medicine)
            if medicine not in target:
                target.append(medicine)
            result['movedWallCabinets'].append(world(124, 120, 0) | dict(sprite=medicine))
        blocked = {(x, y) for (x, y, z), names in tiles.items() if z == 0 and
                   (not any(n in FLOORS for n in names) or any(
                       n not in FLOORS and n != 'roofs_01_22' for n in names))}
        blocked |= route
        programmes = PROGRAM.get(role, PROGRAM['research'])
        for zone, theme in zip(((121, 133, 5, 10), (136, 133, 7, 10)), programmes):
            # The shared decorator handles whole grid objects transactionally.
            groups = defaultdict(list)
            for x, y, sprite in furnish_room(theme, *zone, seed=cx*31+cy, blocked=blocked):
                groups[x, y].append(sprite)
            for (x, y), sprites in groups.items():
                names = tiles.get((x, y, 0), [])
                if not names or any(n.startswith('fixtures_stairs_01_') for n in names):
                    continue
                for sprite in sprites:
                    if sprite not in names:
                        names.append(sprite)
                    result['props'].append(world(x, y, 0) | dict(sprite=sprite, role=theme))
                blocked.add((x, y))
    result['counts'] = {key: len(result[key]) for key in ('signs', 'floorTrail', 'props', 'movedWallCabinets')}
    return result
