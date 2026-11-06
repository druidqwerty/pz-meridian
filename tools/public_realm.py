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

LOT_PARKING_KINDS = {
    'shop', 'generalstore', 'stripmall', 'diner', 'laundry', 'motel',
    'gunshop', 'police', 'firestation', 'apartment', 'midrise',
    'officeblock', 'residentialtower', 'officetower', 'hospital', 'clinic',
    'sanatorium', 'vet', 'lab', 'school', 'kindergarten', 'civic', 'library',
    'museum', 'archive', 'postoffice', 'chapel', 'gym', 'visitor',
    'warehouse', 'workshop', 'garage', 'depot', 'terminal', 'waterworks',
    'scrapyard', 'weighstation', 'military', 'barracks', 'checkpoint', 'gatehouse',
}


def clear_exterior(names):
    """Only terrain, paint and vegetation may yield to a pedestrian surface."""
    return bool(names) and all(n.startswith(('blends_', 'floors_exterior_',
        'street_trafficlines_', 'vegetation_')) for n in names)


def public_realm(tiles, ground, cx, cy, records, site, hard):
    """Author CELL-local site.parking/plazas and building-side parking lots."""
    mask = np.zeros((256, 256), dtype=bool)
    stats = dict(parkingSquares=0, plazaSquares=0, parkingDividers=0,
                 lotParkingLots=0, buildingSigns=[], roadSigns=[], parkingLamps=[])
    road = np.asarray(ground) == 4
    road_curb = dilate(road, 3)
    for key, material, counter in (('parking', CONCRETE, 'parkingSquares'),
                                    ('plazas', PLAZA, 'plazaSquares')):
        for x, y, w, h in site.get(key, ()):
            for xx in range(max(0, x), min(256, x + w)):
                for yy in range(max(0, y), min(256, y + h)):
                    if ground[yy, xx] in (1, 4) or hard[yy, xx]:
                        continue
                    if clear_exterior(tiles.get((xx, yy, 0), ())):
                        tiles[xx, yy, 0] = [material]
                        mask[yy, xx] = True
                        stats[counter] += 1
            if key != 'parking':
                continue
            for line in parking_stalls((x, y, w, h)):
                painted = False
                for xx, yy in line:
                    if 0 <= xx < 256 and 0 <= yy < 256 and mask[yy, xx]:
                        tiles[xx, yy, 0].append(WHITE_W)
                        painted = True
                stats['parkingDividers'] += int(painted)
            for yy in range(y + 4, y + h - 10, 22):
                for xx in range(x + 4, x + w - 4):
                    if 0 <= xx < 256 and 0 <= yy < 256 and mask[yy, xx]:
                        tiles[xx, yy, 0].append(WHITE_N)
            for yy in (y + 1, y + h - 2):
                for xx in range(x + 16, x + w - 8, 32):
                    if (0 <= xx < 256 and 0 <= yy < 256 and mask[yy, xx] and
                            len(tiles[xx, yy, 0]) == 1):
                        tiles[xx, yy, 0].append(PARKING_LAMP)
                        stats['parkingLamps'].append(dict(x=xx, y=yy, z=0, sprite=PARKING_LAMP))

    # Dedicated building-side parking lots for urban, commercial, emergency & civic buildings.
    if records and not site.get('parking'):
        for record in records:
            if record.get('kind') not in LOT_PARKING_KINDS:
                continue
            rx, ry, rw, rh = record['rect']
            rx = rx - cx * 256 if rx >= 256 else rx
            ry = ry - cy * 256 if ry >= 256 else ry
            px, py = rx + rw + 2, ry + 2
            pw, ph = min(18, 238 - px), min(max(12, rh - 4), 238 - py)
            if pw < 10 or ph < 10 or px < 0 or py < 0:
                continue
            if (114 <= px <= 150 or 114 <= px + pw <= 150) and (114 <= py <= 150 or 114 <= py + ph <= 150):
                continue
            placed_lot = 0
            for xx in range(px, px + pw):
                for yy in range(py, py + ph):
                    if ground[yy, xx] in (1, 4) or road_curb[yy, xx] or hard[yy, xx] or mask[yy, xx]:
                        continue
                    if clear_exterior(tiles.get((xx, yy, 0), ())):
                        tiles[xx, yy, 0] = [CONCRETE]
                        mask[yy, xx] = True
                        stats['parkingSquares'] += 1
                        placed_lot += 1
            if placed_lot < 60:
                continue
            stats['lotParkingLots'] += 1
            mid_y = py + ph // 2
            for xx in range(px + 2, px + pw - 2):
                if mask[mid_y, xx]:
                    tiles[xx, mid_y, 0].append(WHITE_N)
            for dx in range(2, pw - 2, 4):
                xx = px + dx
                div = False
                for yy in list(range(py + 1, mid_y)) + list(range(mid_y + 1, py + ph - 1)):
                    if mask[yy, xx]:
                        tiles[xx, yy, 0].append(WHITE_W)
                        div = True
                stats['parkingDividers'] += int(div)
            lx, ly = px + pw - 2, py + 1
            if mask[ly, lx] and len(tiles[lx, ly, 0]) == 1:
                tiles[lx, ly, 0].append(PARKING_LAMP)
                stats['parkingLamps'].append(dict(x=lx, y=ly, z=0, sprite=PARKING_LAMP))

    for record in records:
        x, y, w, h = record['rect']
        x = x - cx * 256 if x >= 256 else x
        y = y - cy * 256 if y >= 256 else y
        if 0 <= x < 256 and 0 <= y < 256:
            signs = place_building_sign(tiles, (x, y, w, h), record['kind'], variant=record.get('variant'))
            stats['buildingSigns'].extend(signs)
            record['signage'] = signs
    shoulder = dilate(road, 6) & ~dilate(road, 3)
    for yy in range(12, 245, 64):
        for xx in range(12, 245, 64):
            choices = [(x, y) for y in range(yy - 6, yy + 7) for x in range(xx - 6, xx + 7)
                       if shoulder[y, x] and not hard[y, x] and not mask[y, x]
                       and clear_exterior(tiles.get((x, y, 0), ()))]
            if not choices:
                continue
            x, y = min(choices, key=lambda p: abs(p[0] - xx) + abs(p[1] - yy))
            sprite = STREETNAME if (cx + cy + xx + yy) % 2 else STOP
            tiles[x, y, 0] = [CONCRETE, sprite]
            stats['roadSigns'].append(dict(x=x, y=y, z=0, sprite=sprite))
    return stats, mask
