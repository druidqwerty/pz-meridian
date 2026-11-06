"""Prepare private urban-content oracle targets; never an implementation claim.

Run after generation: python tools/urban_targets.py
The JSON list uses playtest.py's visit/walk fields and its private ``lighting``
oracle. The companion checklist separates executed checks from preparation;
simply visiting a room is not silently treated as a successful light test.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def absolute(point, record):
    """Promote optional cell-local diagnostic coordinates, preserving world ones."""
    if isinstance(point, dict):
        x, y, z = point['x'], point['y'], point.get('z', 0)
    else:
        x, y, z = point
    if 0 <= x < 256 and 0 <= y < 256:
        x += record['rect'][0] // 256 * 256
        y += record['rect'][1] // 256 * 256
    return dict(x=x, y=y, z=z)


def visit(record, label=None, z=0):
    point = absolute(record['spawn'], record)
    point['z'] = z
    return dict(name=label or f"{record['site']} {record['kind']}", **point,
                room=True, noViewpoint=True, zoom=1.25)


def prepare(manifest):
    records = [r for cell in manifest['cells'] for r in cell.get('records', [])]
    if not records:
        raise ValueError('Manifest has no authored building records')
    settlements = {s['name']: s for s in manifest.get('settlements', [])}
    distance = lambda r: settlements.get(r['site'], {}).get('fraction', 1)
    ordered = sorted(records, key=lambda r: (distance(r), r['rect']))
    targets = []
    selected = set()

    def add(record, label=None):
        key = (*record['rect'][:2], record['kind'])
        if key in selected:
            return
        selected.add(key)
        targets.append(visit(record, label))

    first = [r for r in ordered if r['site'] == 'Last Light']
    if first:
        add(next((r for r in first if r['kind'] == 'cottage'), first[0]),
            'Last Light furnished home')
    for label, kinds in (
        ('Early garage', {'garage', 'workshop'}),
        ('Early police station', {'police', 'sheriff'}),
        ('Early school', {'school'}),
        ('Small retail frontage', {'shop', 'cornerstore', 'stripmall', 'retailrow'}),
        ('Large shopping centre', {'bigboxmall'}),
        ('Gun shop', {'gunshop'}),
        ('Guard hut or checkpoint', {'guardhut', 'checkpoint', 'gatehouse'}),
    ):
        found = next((r for r in ordered if r['kind'] in kinds), None)
        if found:
            add(found, label)
    middle = [r for r in ordered if .20 <= distance(r) < .65]
    later = [r for r in ordered if .65 <= distance(r) < 1]
    if middle:
        add(max(middle, key=lambda r: r['levels']), 'Regional centre height sample')
    if later:
        add(max(later, key=lambda r: r['levels']), 'Late approach height sample')
    final = [r for r in ordered if r['site'] == 'Meridian']
    if final:
        tallest = max(final, key=lambda r: r['levels'])
        add(tallest, 'Meridian tallest tower ground floor')
        # A physical flight test is included only when architecture supplies it.
        # Do not guess a staircase from a repeated prototype's former position.
        flights = tallest.get('stairTests', [])
        top=visit(tallest, 'Meridian tower top occupied floor', tallest['levels'] - 1)
        top['zoom']=2.0
        if flights:
            top.update(absolute(flights[-1].get('to', flights[-1].get('end')), tallest))
        targets.append(top)
        for index in sorted({0, len(flights) - 1}) if flights else ():
            flight = flights[index]
            start = absolute(flight.get('from', flight.get('start')), tallest)
            end = absolute(flight.get('to', flight.get('end')), tallest)
            targets.append(dict(name=f'Meridian tower actual flight {index + 1}',
                                **start, room=True, walkTo=end, noViewpoint=True))
    for record in (first[:1] + ([max(final, key=lambda r: r['levels'])] if final else [])):
        switches = [s for s in record.get('lighting', []) if s.get('kind') == 'switch']
        if switches:
            target = visit(record, record['site'] + ' native room-light toggle')
            target['lighting'] = absolute(switches[0], record)
            target['lighting']['sprite'] = switches[0]['sprite']
            targets.append(target)
    safe = manifest.get('safeCity', [48128, 1024, 49152, 2048])
    # Approach and inner side of the west gate: neither target is on the wall.
    gate_y = 1536
    targets.extend([
        dict(name='Meridian west fortification approach', x=safe[0] - 20,
             y=gate_y, z=0, noViewpoint=True, zoom=2.0),
        dict(name='Meridian west gate inner court', x=safe[0] + 28,
             y=gate_y, z=0, safeSurface=True, noViewpoint=True, zoom=2.0),
    ])
    for cell in manifest['cells']:
        if any(r['kind']=='bigboxmall' for r in cell.get('records', [])):
            lamps=(cell.get('streetscape') or {}).get('publicRealm', {}).get('parkingLamps', [])
            if lamps:
                lamp=lamps[0];cx,cy=cell['cell']
                targets.append(dict(name='Shopping centre parking apron',
                    x=cx*256+lamp['x']+2,y=cy*256+lamp['y']+2,z=0,noViewpoint=True,zoom=2.5))
                break
    bastion=next((c['cityWall'] for c in manifest['cells']
                  if c.get('cityWall') and c['cityWall'].get('stairs')),None)
    if bastion:
        bottom=bastion['stairs']['bottom'];top=bastion['stairs']['top']
        targets.append(dict(name='Fortification first actual stair flight',
            x=bottom[0],y=bottom[1],z=bottom[2],room=True,safeSurface=True,
            walkTo=dict(x=top[0],y=top[1],z=1),noViewpoint=True,zoom=1.5))
        targets.append(dict(name='Fortification crown and city skyline',
            x=top[0],y=top[1],z=top[2],safeSurface=True,noViewpoint=True,zoom=2.5))
    public=next((c for c in manifest['cells'] if c['cell']==[188,5] and c.get('bunker')),None)
    if public:
        e=next(e for e in public['bunker']['entrances'] if e['role']=='public')
        targets.append(dict(name='Public bunker entrance actual descent',x=e['x'],y=e['y'],z=0,
            room=True,safeSurface=True,walkTo=dict(x=e['bottom'][0],y=e['bottom'][1],z=-1),
            noViewpoint=True,zoom=1.25))
        switches=[s for s in public['bunker'].get('lighting', [])
                  if s.get('kind')=='switch' and s['z']==-1]
        if switches:
            s=switches[0]
            location=dict(x=188*256+s['x'],y=5*256+s['y'],z=-1)
            targets.append(dict(name='B1 native room-light toggle',**location,room=True,
                infected=True,lighting=location|dict(sprite=s['sprite']),noViewpoint=True,zoom=1.25))
    summaries = []
    for name, site in settlements.items():
        subset = [r for r in records if r['site'] == name]
        if not subset or site.get('kind') == 'service':
            continue
        heights = Counter(r['levels'] for r in subset)
        summaries.append(dict(site=name, fraction=site.get('fraction'),
            buildings=len(subset), kinds=dict(sorted(Counter(r['kind'] for r in subset).items())),
            floorCounts=dict(sorted(heights.items())), maxFloors=max(heights),
            highrises6Plus=sum(n for height, n in heights.items() if height >= 6)))
    checklist = dict(
        kind='Prepared checks, not executed evidence',
        requiresOracleSupport=['lighting: native IsoLightSwitch toggle off/on and restore; implemented in playtest.py'],
        settlements=summaries,
        manualChecks=[
            'Inspect representative first-home furniture facing and complete multi-tile pieces.',
            'Switch diagnostic torch OFF; set lab time to night; capture native light ON and OFF.',
            'Inspect same-room switch native class, metaobject, activation change and restoration.',
            'Compare early/middle/late isometric streets; facades and room plans must differ.',
            'Capture final city skyline from more than one side and multiple city districts.',
            'Inspect fortification top, cross-section, connected corners and deep west gate.',
            'Walk up and down real tower/wall stairs; teleport does not establish traversal.',
            'Confirm sanctuary applies only to surface, preserving infected basement levels.',
        ],
        warnings=[])
    if final and max(r['levels'] for r in final) < 6:
        checklist['warnings'].append('Final city has no six-plus-floor skyline in this manifest.')
    if not any('lighting' in t for t in targets):
        checklist['warnings'].append('No lighting coordinates emitted; native light checks require manual targets.')
    if final and not max(final, key=lambda r: r['levels']).get('stairTests'):
        checklist['warnings'].append('Tallest tower has no explicit stairTests metadata; supply physical endpoints.')
    return targets, checklist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'build/manifest.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/test-urban-content.json')
    args = parser.parse_args()
    targets, checklist = prepare(json.loads(args.manifest.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(targets, indent=2), encoding='utf-8')
    companion = args.output.with_suffix('.checklist.json')
    companion.write_text(json.dumps(checklist, indent=2), encoding='utf-8')
    print(f'{len(targets)} visit targets: {args.output}')
    print(f'Acceptance checklist: {companion}')
    for warning in checklist['warnings']:
        print('PREPARATION WARNING: ' + warning)


if __name__ == '__main__':
    main()
