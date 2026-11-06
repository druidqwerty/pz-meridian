"""Prepare density QA from compiled RoomDefs and manifest furnishing receipts.

Preparation is not live-game evidence. No game, install or save is changed.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from functools import lru_cache
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_architecture import sprites, combine
from map_binary import read_cell


def free_room_points(data, number, db):
    """Conservative observer squares: no furniture, stairs or solid objects."""
    room = data['rooms'][number]
    z = room['level']
    points = set()
    for (x, y, zz), index in data['room_ids'].items():
        if index != number or zz != z:
            continue
        names = data['tiles'].get((x, y, z), [])
        flags = combine(db, names)
        if 'solidfloor' not in flags or any(k in flags for k in ('solid', 'solidtrans')):
            continue
        if any(k.startswith('stairs') for k in flags):
            continue
        if any('IsMoveAble' in db[n] and 'solidfloor' not in db[n]
               and db[n].get('MoveType') != 'WallObject'
               and not any(k in db[n] for k in ('doorN', 'doorW', 'windowN', 'windowW'))
               for n in names):
            continue
        points.add((x, y))
    return points


def walk_pair(data, number, db):
    """Find centre observer and an ordinary short aisle walk in the same room."""
    free = free_room_points(data, number, db)
    if not free:
        raise ValueError('Actual native room has no free observer square')
    rects = data['rooms'][number]['rects']
    x, y, w, h = max(rects, key=lambda r: r[2] * r[3])
    origin = min(free, key=lambda p: ((p[0]-x-w/2)**2+(p[1]-y-h/2)**2, p))
    pending = deque([origin]); distance = {origin: 0}
    z = data['rooms'][number]['level']
    while pending:
        current = pending.popleft()
        if distance[current] >= 10:
            continue
        for dx, dy, direction in ((1, 0, 'W'), (-1, 0, 'W'), (0, 1, 'N'), (0, -1, 'N')):
            point = current[0]+dx, current[1]+dy
            if point not in free or point in distance:
                continue
            edge = max(current[0], point[0]), max(current[1], point[1]), z
            flags = combine(db, data['tiles'].get(edge, []))
            if any(k+direction in flags for k in ('Wall', 'Window', 'DoorWall', 'collide')):
                continue
            distance[point] = distance[current]+1
            pending.append(point)
    destination = max(distance, key=lambda p: (distance[p], p))
    if distance[destination] < 4:
        raise ValueError('Actual room lacks a four-tile clear connected aisle')
    return origin, destination, distance[destination]


def furnishing_entries(manifest):
    for cell in manifest['cells']:
        for record in cell.get('records', []):
            for receipt in record.get('furnishing', []):
                yield cell['cell'], record, receipt
        bunker = cell.get('bunker')
        if bunker:
            for receipt in bunker.get('furnishing', []):
                yield cell['cell'], bunker, receipt


def match_room(data, receipt, cx, cy):
    x, y, w, h = receipt['rect']
    local = x-cx*256, y-cy*256, w, h
    matches = [i for i, room in enumerate(data['rooms'])
               if room['level'] == receipt['z'] and room['name'] == receipt['lootRole']
               and local in room['rects']]
    if len(matches) != 1:
        raise ValueError(f'Furnishing receipt does not identify one native RoomDef: {receipt}')
    return matches[0]


def programme_candidates(entries, names, purposes, underground, safe):
    """Native loot names do not identify a furnishing programme by themselves.

    A nursery intentionally uses classroom loot; restaurant kitchens use kitchen
    loot, while public dining halls may use hall/livingroom. Require both fields
    so QA cannot silently certify the wrong activity under a convenient label.
    """
    candidates = [entry for entry in entries if entry[2]['lootRole'] in names
                  and entry[2].get('purpose') in purposes
                  and (entry[2]['z'] == -1 if underground else entry[2]['z'] == 0)]
    if underground:
        candidates = [entry for entry in candidates
                      if safe[0] <= entry[2]['rect'][0] < safe[2]
                      and safe[1] <= entry[2]['rect'][1] < safe[3]]
    return candidates


def prepare(manifest, folder, db=None):
    db = sprites() if db is None else db
    entries = list(furnishing_entries(manifest))
    zoned = [entry for entry in entries if entry[2]['policy'] == 'zoned']
    if not zoned:
        raise ValueError('Manifest has no zoned furnishing receipts; build the new candidate first')

    @lru_cache(maxsize=8)
    def native(cx, cy):
        return read_cell(folder, cx, cy)

    targets, selected = [], []
    roles = (
        ('Large office activity zones', {'office'}, {'office'}, False),
        ('School classroom activity zones', {'classroom'}, {'classroom'}, False),
        ('Large retail sales floor', {'departmentstore', 'grocery'}, {'grocery'}, False),
        ('Public dining activity zones', {'hall', 'livingroom', 'cafe', 'restaurant'}, {'dining'}, False),
        ('Storage activity and clear aisles', {'storage', 'armystorage'}, {'storage', 'armystorage'}, False),
        ('B1 public kitchen activity zones', {'kitchen', 'restaurantkitchen'}, {'restaurantkitchen'}, True),
        ('B1 dormitory activity zones', {'bedroom', 'dormitory'}, {'dormitory'}, True),
    )
    for label, names, purposes, underground in roles:
        candidates = programme_candidates(zoned, names, purposes, underground, manifest['safeCity'])
        if not candidates:
            raise ValueError(f'Missing required representative zoned programme: {label}')
        cell, record, receipt = min(candidates, key=lambda entry:
            (-entry[2]['floorSquares'], entry[2]['rect'], entry[2]['z']))
        if not receipt['accepted']:
            raise ValueError(f'Selected programme not accepted: {label}: {receipt["warnings"]}')
        cx, cy = cell; data = native(cx, cy)
        number = match_room(data, receipt, cx, cy)
        origin, end, distance = walk_pair(data, number, db)
        target = dict(name=label, x=cx*256+origin[0], y=cy*256+origin[1], z=receipt['z'],
                      room=True, noViewpoint=True, zoom=2.0 if receipt['floorSquares'] > 600 else 1.5,
                      walkTo=dict(x=cx*256+end[0], y=cy*256+end[1], z=receipt['z']),
                      walkLabel='activity_aisle_traversal')
        if underground:
            target['infected'] = True
        elif (manifest['safeCity'][0] <= receipt['rect'][0] < manifest['safeCity'][2]
              and manifest['safeCity'][1] <= receipt['rect'][1] < manifest['safeCity'][3]):
            target['safeSurface'] = True
        targets.append(target)
        selected.append(dict(label=label, cell=cell, nativeRoomIndex=number,
                             nativeRoom=data['rooms'][number], furnishing=receipt,
                             preparedWalkDistance=distance))
        # Test one real native switch in a large surface room and one in B1.
        if label in ('Large office activity zones', 'B1 public kitchen activity zones'):
            switches = []
            for s in record.get('lighting', []):
                if s.get('kind') != 'switch' or s['z'] != receipt['z']:
                    continue
                sx, sy = s['x'], s['y']
                if 0 <= sx < 256 and 0 <= sy < 256:
                    sx += cx*256; sy += cy*256
                if data['room_ids'].get((sx-cx*256, sy-cy*256, s['z'])) == number:
                    switches.append(s | dict(x=sx, y=sy))
            if not switches:
                raise ValueError(f'Selected native room lacks a recorded switch: {label}')
            s = switches[0]
            points = free_room_points(data, number, db)
            near = min(points, key=lambda p: (p[0]+cx*256-s['x'])**2+(p[1]+cy*256-s['y'])**2)
            targets.append(dict(name=label+' native night switch', x=cx*256+near[0],
                y=cy*256+near[1], z=receipt['z'], room=True, noViewpoint=True, zoom=1.5,
                lighting={k:s[k] for k in ('x', 'y', 'z', 'sprite')}))
    records = [r for cell in manifest['cells'] for r in cell.get('records', [])]
    towers = [r for r in records if r.get('site') == 'Meridian' and r.get('stairTests')]
    if not towers:
        raise ValueError('Manifest lacks an actual Meridian tower stair test')
    tower = max(towers, key=lambda r: r['levels'])
    flight = tower['stairTests'][0]
    start = flight.get('from', flight.get('start')); end = flight.get('to', flight.get('end'))
    targets.append(dict(name='Density candidate tower ordinary stair',
        x=start[0], y=start[1], z=start[2], room=True, safeSurface=True,
        walkTo=dict(x=end[0], y=end[1], z=end[2]), noViewpoint=True, zoom=1.5))
    public = [(cell, entry) for cell in manifest['cells'] if cell.get('bunker')
              for entry in cell['bunker'].get('entrances', []) if entry.get('role') == 'public']
    if not public:
        raise ValueError('Manifest lacks a public bunker entrance')
    _, entrance = min(public, key=lambda pair: (pair[1]['x'], pair[1]['y']))
    end = entrance['bottom']
    targets.append(dict(name='Density candidate public bunker ordinary descent',
        x=entrance['x'], y=entrance['y'], z=0, room=True, safeSurface=True,
        walkTo=dict(x=end[0], y=end[1], z=-1), noViewpoint=True, zoom=1.5))
    return targets, dict(kind='Prepared density checks, NOT executed evidence',
        policies=dict(Counter(entry[2]['policy'] for entry in entries)),
        zonedRooms=len(zoned), unacceptedZoned=sum(not e[2]['accepted'] for e in zoned),
        warningCounts=dict(Counter(w for entry in zoned for w in entry[2]['warnings'])),
        selected=selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'build/manifest.json')
    parser.add_argument('--native', type=Path, default=ROOT/'mod/common/media/maps/Meridian')
    parser.add_argument('--output', type=Path, default=ROOT/'build/test-density-final.json')
    args = parser.parse_args()
    targets, checklist = prepare(json.loads(args.manifest.read_text(encoding='utf-8')), args.native)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(targets, indent=2), encoding='utf-8')
    companion = args.output.with_suffix('.checklist.json')
    companion.write_text(json.dumps(checklist, indent=2), encoding='utf-8')
    print(f'{len(targets)} compiled-room density, native light and stair targets: {args.output}')
    print(f'Prepared coverage (not executed evidence): {companion}')


if __name__ == '__main__':
    main()
