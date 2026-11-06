"""Native B42 electrical rooms: wall switches, type-7 metaobjects and fixtures.

Verified jar oracle: IsoRoom.hasLightSwitches checks RoomDef.objects type 7;
IsoRoom.createLights creates room lights for native RoomRects. RGB sprite lamps
are separate IsoLightSwitch objects with their own bulbs, not fake floor decor.
"""

SWITCHES = {'N': 0, 'W': 1, 'E': 2, 'S': 3}
LAMPS = {'N': 61, 'W': 60, 'E': 62, 'S': 63}


WALL_PREFIXES = (
    'walls_exterior_house_', 'walls_commercial_', 'walls_exterior_wooden_',
    'walls_garage_', 'walls_interior_house_', 'walls_interior_bathroom_', 'walls_logs_',
)


def _wall(names, direction):
    # All verified wall palettes use base % 16 in (0, 4): solid W is +0, solid N is +1.
    expected = (1, 5) if direction == 'N' else (0, 4)
    for n in names:
        if not n.startswith(WALL_PREFIXES):
            continue
        idx = int(n.rsplit('_', 1)[1])
        if n.startswith('walls_garage_01_') and idx < 16:
            continue
        if idx % 16 in expected:
            return True
    return False


def place_room_lighting(tiles, room, *, blocked=()):
    """Add a genuine room circuit and backed fixtures; return diagnostic coords.

    Coordinates in RoomDef.objects are CELL-local, as in .lotheader, not relative
    to the rectangle. Call after geometry, before writing the native cell. An
    idempotent call neither duplicates type7 objects nor physical fixtures.
    """
    z = room.get('level', room.get('z', 0))
    blocked = {(p[0], p[1]) for p in blocked}
    points = {(xx, yy) for x, y, w, h in room['rects']
              for xx in range(x, x+w) for yy in range(y, y+h)}
    existing = []
    switch_names = {'lighting_indoor_01_'+str(n) for n in SWITCHES.values()}
    lamp_names = {'lighting_indoor_02_'+str(n) for n in LAMPS.values()}
    for x, y in points:
        for sprite in tiles.get((x, y, z), ()):
            if sprite in switch_names | lamp_names:
                existing.append(dict(x=x, y=y, z=z, sprite=sprite,
                    kind='switch' if sprite in switch_names else 'lamp'))
    if ({p['kind'] for p in existing} == {'switch', 'lamp'} and
            any(obj[0] == 7 for obj in room.get('objects', ()))):
        return sorted(existing, key=lambda p: (p['kind'], p['y'], p['x']))
    candidates = []
    for x, y in sorted(points, key=lambda p: (p[1], p[0])):
        if (x, y) in blocked or (x, y, z) not in tiles:
            continue
        # Back-face E/S fixtures are valid native objects, but survive the
        # foreground wall cutaway and look like floating furniture. Prefer
        # only a directly present N/W support for readable isometric interiors.
        for d, wx, wy, wd in (('N', x, y, 'N'), ('W', x, y, 'W')):
            if (wx, wy) not in points or (wx, wy) == (x, y):
                if _wall(tiles.get((wx, wy, z), ()), wd):
                    candidates.append((x, y, d))
                    break
    if not candidates:
        raise ValueError(f"Room without a switch-supporting solid wall: {room['name']} z{z}")
    # Prefer a low-clutter segment; avoid attaching switch behind a cupboard.
    candidates.sort(key=lambda p: (len(tiles[p[0], p[1], z]), p[1], p[0]))
    x, y, d = candidates[0]
    objects = room.setdefault('objects', [])
    if not any(obj[0] == 7 for obj in objects):
        objects.append((7, x, y))
    result = []
    def add(x, y, d, kind):
        sprite = ('lighting_indoor_01_' + str(SWITCHES[d]) if kind == 'switch'
                  else 'lighting_indoor_02_' + str(LAMPS[d]))
        names = tiles.setdefault((x, y, z), [])
        if sprite not in names:
            names.append(sprite)
        result.append(dict(x=x, y=y, z=z, sprite=sprite, kind=kind))
    add(x, y, d, 'switch')
    # Native ambient room circuit covers every RoomRect. Visible fixtures are
    # spread around large halls at >=8-tile spacing, not one lamp in a corner.
    wanted = max(1, min(48, (len(points)+119)//120))
    chosen = []
    for xx, yy, dd in candidates:
        if (xx, yy) == (x, y) and len(candidates) > 1:
            continue
        if any(abs(xx-a)+abs(yy-b) < 8 for a, b in chosen):
            continue
        add(xx, yy, dd, 'lamp')
        chosen.append((xx, yy))
        if len(chosen) >= wanted:
            break
    return result
