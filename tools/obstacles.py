"""Deterministic vanilla salvage checkpoints, not painted collision facades.

Sprite capabilities are checked against the installed B42 tile-definition files
by tests/test_obstacles.py. The native map contains ordinary movable/scrappable
objects: vanilla tool, skill and inventory rules remain authoritative.
"""
from world import ROUTE

ROADBLOCK_NS = 'construction_01_8'
ROADBLOCK_EW = 'construction_01_9'
CRATE = 'carpentry_01_16'
PALLET = 'construction_01_4'
GRINDER = 'construction_01_6'
LOCKER = 'furniture_storage_02_0'
SALVAGE_SPRITES = (ROADBLOCK_NS, ROADBLOCK_EW, CRATE, PALLET, GRINDER, LOCKER)


def road_encounters():
    """Plan once per cell from a small route-wide list; skip the safe start."""
    result = []
    for index, distance in enumerate(range(1800, int(ROUTE.length)-400, 1800)):
        p = ROUTE.interpolate(distance)
        a, b = ROUTE.interpolate(distance-8), ROUTE.interpolate(distance+8)
        horizontal = abs(b.x-a.x) > abs(b.y-a.y)
        x, y = round(p.x), round(p.y)
        if not (20 < (x if horizontal else y) % 256 < 236):
            continue
        result.append(dict(id=index, x=x, y=y, distance=distance,
            horizontal=horizontal, kind=('roadworks', 'evacuation', 'checkpoint')[index % 3]))
    return result


ENCOUNTERS = road_encounters()


def dress_obstacles(cx, cy, ground, tiles, site=None):
    """Return encounter/object metadata; preserve a five-tile asphalt passage.

    Call after landscaping and structures, before native serialization. Nothing
    is placed over structures, pumps, walls or other authored furniture.
    """
    if site and site.get('id') == 0:
        return dict(encounters=[], objects=[])
    encounters, objects = [], []
    for spec in ENCOUNTERS:
        if not (cx*256-12 <= spec['x'] < (cx+1)*256+12 and
                cy*256-12 <= spec['y'] < (cy+1)*256+12):
            continue
        x, y = spec['x']-cx*256, spec['y']-cy*256
        horizontal = spec['horizontal']
        sprite = ROADBLOCK_NS if horizontal else ROADBLOCK_EW
        # Endpoint guard; wide streams/causeways must not become roadwork lots.
        if 0 <= x < 256 and 0 <= y < 256 and ground[y, x] != 4:
            continue
        placed = []
        def add(along, across, name, kind):
            xx, yy = (x+along, y+across) if horizontal else (x+across, y+along)
            key = xx, yy, 0
            if not (0 <= xx < 256 and 0 <= yy < 256) or ground[yy, xx] == 1:
                return
            names = tiles.get(key, [])
            if not names or any(not n.startswith(('blends_', 'street_trafficlines_')) for n in names):
                return
            tiles[key] = names + [name]
            record = dict(x=cx*256+xx, y=cy*256+yy, z=0, sprite=name, kind=kind)
            objects.append(record); placed.append(record)
        # The narrowing is real, but no tools or skills are required to continue.
        for across in (-6, -5, -4, -3, 3, 4, 5, 6):
            add(0, across, sprite, 'roadblock')
        if spec['kind'] == 'roadworks':
            for along, across, name in ((-4, -10, PALLET), (-3, -10, PALLET),
                                         (4, 10, GRINDER), (5, 10, PALLET)):
                add(along, across, name, 'repair_supplies')
        elif spec['kind'] == 'evacuation':
            for along, across in ((-3, -9), (-2, -9), (2, 9), (3, 9), (4, 9)):
                add(along, across, CRATE, 'abandoned_supplies')
        else:
            for along in (-4, -3, 3, 4):
                add(along, -9, LOCKER, 'checkpoint_locker')
                add(along, 9, CRATE, 'checkpoint_supplies')
        if placed and 0 <= x < 256 and 0 <= y < 256:
            encounters.append(dict(**spec, gapWidth=5,
                gap=[dict(x=spec['x']+(0 if horizontal else n),
                          y=spec['y']+(n if horizontal else 0), z=0) for n in range(-2, 3)],
                anchorObjects=len(placed)))
    return dict(encounters=encounters, objects=objects)


def tunnel_obstacles(tiles, cx, cy, z):
    """Gallery salvage piles leave two+ clear lanes and all seam mouths open."""
    objects = []
    for along in (72, 184):
        for across in (126, 127, 130, 131):
            for x, y in ((along, across), (across, along)):
                name = LOCKER if (cx+cy+along+across+z) % 3 == 0 else CRATE
                if len(tiles.get((x, y, z), [])) != 1:
                    continue
                tiles[x, y, z].append(name)
                objects.append(dict(x=cx*256+x, y=cy*256+y, z=z,
                                    sprite=name, kind='tunnel_barricade'))
    return objects
