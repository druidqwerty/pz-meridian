"""Native plaza/parking hardscape, facade identity and off-lane road signs."""
import numpy as np
from public_geometry import parking_stalls, dilate
from building_signs import place_building_sign

CONCRETE = 'floors_exterior_tilesandstone_01_0'
PLAZA = 'floors_exterior_tilesandstone_01_1'
WHITE_W = 'street_trafficlines_01_0'
WHITE_N = 'street_trafficlines_01_2'
STOP = 'street_decoration_01_0'
STREETNAME = 'street_decoration_01_22'
PARKING_LAMP = 'lighting_outdoor_01_0'


def clear_exterior(names):
    """Only terrain, paint and vegetation may yield to a pedestrian surface."""
    return bool(names) and all(n.startswith(('blends_', 'floors_exterior_',
        'street_trafficlines_', 'vegetation_')) for n in names)


def public_realm(tiles, ground, cx, cy, records, site, hard):
    """Author CELL-local site.parking/plazas without eating native roads/rooms.

    Returns diagnostics and hardscape mask; designated parking has two-sided
    banks, eight-tile drive aisles and a broad perimeter circulation zone.
    """
    mask = np.zeros((256, 256), dtype=bool)
    stats = dict(parkingSquares=0, plazaSquares=0, parkingDividers=0,
                 buildingSigns=[], roadSigns=[], parkingLamps=[])
    for key, material, counter in (('parking', CONCRETE, 'parkingSquares'),
                                    ('plazas', PLAZA, 'plazaSquares')):
        for x, y, w, h in site.get(key, ()):
            for xx in range(max(0,x), min(256,x+w)):
                for yy in range(max(0,y), min(256,y+h)):
                    if ground[yy,xx] in (1,4) or hard[yy,xx]:
                        continue
                    if clear_exterior(tiles.get((xx,yy,0),())):
                        tiles[xx,yy,0] = [material]
                        mask[yy,xx] = True
                        stats[counter] += 1
            if key != 'parking':
                continue
            for line in parking_stalls((x,y,w,h)):
                painted = False
                for xx, yy in line:
                    if 0 <= xx < 256 and 0 <= yy < 256 and mask[yy,xx]:
                        tiles[xx,yy,0].append(WHITE_W)
                        painted = True
                stats['parkingDividers'] += int(painted)
            # Long bank-end markings make stalls legible rather than endless
            # short white strokes; entrances/perimeter are always unpainted.
            for yy in range(y+4, y+h-10, 22):
                for xx in range(x+4, x+w-4):
                    if 0 <= xx < 256 and 0 <= yy < 256 and mask[yy,xx]:
                        tiles[xx,yy,0].append(WHITE_N)
            # Lit perimeter, not solid lamp posts across drive aisles/stall bays.
            for yy in (y+1,y+h-2):
                for xx in range(x+16,x+w-8,32):
                    if (0<=xx<256 and 0<=yy<256 and mask[yy,xx] and
                            len(tiles[xx,yy,0])==1):
                        tiles[xx,yy,0].append(PARKING_LAMP)
                        stats['parkingLamps'].append(dict(x=xx,y=yy,z=0,sprite=PARKING_LAMP))
    for record in records:
        x,y,w,h = record['rect']
        x = x-cx*256 if x >= 256 else x
        y = y-cy*256 if y >= 256 else y
        if 0 <= x < 256 and 0 <= y < 256:
            signs = place_building_sign(tiles, (x,y,w,h), record['kind'])
            stats['buildingSigns'].extend(signs)
            record['signage'] = signs
    road = np.asarray(ground) == 4
    shoulder = dilate(road, 6) & ~dilate(road, 3)
    # Deterministic set-back corner posts: they cannot block either asphalt or
    # the two-tile sidewalk. Actual street signs carry vanilla hit-by-car props.
    for yy in range(12, 245, 64):
        for xx in range(12, 245, 64):
            choices = [(x,y) for y in range(yy-6,yy+7) for x in range(xx-6,xx+7)
                       if shoulder[y,x] and not hard[y,x] and not mask[y,x]
                       and clear_exterior(tiles.get((x,y,0),()))]
            if not choices:
                continue
            x,y = min(choices,key=lambda p:abs(p[0]-xx)+abs(p[1]-yy))
            sprite = STREETNAME if (cx+cy+xx+yy)%2 else STOP
            tiles[x,y,0] = [CONCRETE, sprite]
            stats['roadSigns'].append(dict(x=x,y=y,z=0,sprite=sprite))
    return stats, mask
