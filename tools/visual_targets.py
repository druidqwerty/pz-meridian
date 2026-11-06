"""Private actual-room visual targets read from compiled native geometry.

Unlike generic building spawn points, these deliberately stand inside furnished
rooms. No game is launched and no product data is changed by this builder.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_architecture import sprites, combine
from map_binary import read_cell


def prepare(manifest, folder, condensed=False):
    props = sprites()
    records = [r for c in manifest['cells'] for r in c.get('records', [])]

    @lru_cache(maxsize=5)
    def cell(cx, cy):
        return read_cell(folder, cx, cy)

    def room_visit(record, preferred, label, z=0, light=False):
        wx, wy, w, h = record['rect'];cx, cy = wx//256, wy//256
        local_x, local_y = wx%256, wy%256
        data = cell(cx, cy)
        candidates = [(index, room) for index, room in enumerate(data['rooms'])
            if room['level']==z and room['name']!='hall' and all(
                local_x<=x and local_y<=y and x+rw<=local_x+w and y+rh<=local_y+h
                for x, y, rw, rh in room['rects'])]
        if not candidates:
            raise ValueError(f'No actual furnished RoomDef: {label}')
        number, room = min(candidates, key=lambda pair:
            preferred.index(pair[1]['name']) if pair[1]['name'] in preferred else len(preferred))
        x, y, rw, rh = room['rects'][0]
        points = []
        for xx in range(x, x+rw):
            for yy in range(y, y+rh):
                if data['room_ids'].get((xx, yy, z))!=number:
                    continue
                names=data['tiles'].get((xx, yy, z), [])
                flags=combine(props, names)
                if 'solidfloor' not in flags or any(k in flags for k in ('solid','solidtrans')):
                    continue
                if any(n.startswith('fixtures_stairs_01_') for n in names):
                    continue
                if any('IsMoveAble' in props[n] and 'solidfloor' not in props[n] and
                       props[n].get('MoveType')!='WallObject' and
                       not any(k in props[n] for k in ('doorN','doorW','windowN','windowW')) for n in names):
                    continue
                points.append((xx, yy))
        if not points:
            raise ValueError(f'No free observer square: {label}')
        xx, yy=min(points, key=lambda p:(p[0]-(x+rw/2))**2+(p[1]-(y+rh/2))**2)
        result=dict(name=label,x=cx*256+xx,y=cy*256+yy,z=z,room=True,noViewpoint=True,zoom=1.5)
        if light:
            switches=[s for s in record['lighting'] if s.get('kind')=='switch' and s['z']==z and
                data['room_ids'].get((s['x']-cx*256,s['y']-cy*256,z))==number]
            if not switches:
                raise ValueError(f'Actual room lacks recorded native switch: {label}')
            s=switches[0]
            result['lighting']={key:s[key] for key in ('x','y','z','sprite')}
        return result

    home=next(r for r in records if r['site']=='Last Light' and r['kind']=='cottage')
    mall=min((r for r in records if r['kind']=='bigboxmall'), key=lambda r:abs(r['spawn'][1]-48640))
    gun=next(r for r in records if r['site']=='Last Light' and r['kind']=='gunshop')
    tower=max((r for r in records if r['site']=='Meridian'),key=lambda r:r['levels'])
    if condensed:
        targets=[room_visit(home,['kitchen'],'Final cottage kitchen and native night lighting',light=True),
            room_visit(home,['bedroom'],'Final cottage bed and furniture facing'),
            room_visit(home,['livingroom'],'Final cottage living room'),
            room_visit(tower,['office','livingroom','bedroom'],'Final tower room and native night lighting',0,True)]
        flights=tower['stairTests']
        for index in (0,len(flights)-1):
            flight=flights[index];start=flight.get('from',flight.get('start'));end=flight.get('to',flight.get('end'))
            targets.append(dict(name=f'Final tower actual flight {index+1}',x=start[0],y=start[1],z=start[2],
                room=True,safeSurface=True,walkTo=dict(x=end[0],y=end[1],z=end[2]),noViewpoint=True,zoom=1.5))
        bastion=next(c['cityWall'] for c in manifest['cells'] if c.get('cityWall') and c['cityWall'].get('stairs'))
        bottom=bastion['stairs']['bottom'];top=bastion['stairs']['top']
        targets.append(dict(name='Final wall upper actual flight',x=bottom[0],y=bottom[1],z=top[2]-1,
            room=True,safeSurface=True,walkTo=dict(x=top[0],y=top[1],z=top[2]),noViewpoint=True,zoom=1.5))
        targets.append(dict(name='Final wall crown and city view',x=top[0],y=top[1],z=top[2],
            safeSurface=True,noViewpoint=True,zoom=2.5))
        cx,cy=mall['rect'][0]//256,mall['rect'][1]//256
        mall_cell=next(c for c in manifest['cells'] if c['cell']==[cx,cy])
        lamp=mall_cell['streetscape']['publicRealm']['parkingLamps'][0]
        targets.append(dict(name='Final mall parking apron',x=cx*256+lamp['x']+2,
            y=cy*256+lamp['y']+2,z=0,noViewpoint=True,zoom=2.5))
        bunker=next(c['bunker'] for c in manifest['cells'] if c['cell']==[188,5])
        e=next(e for e in bunker['entrances'] if e['role']=='public')
        targets.append(dict(name='Final public bunker actual descent',x=e['x'],y=e['y'],z=0,
            room=True,safeSurface=True,walkTo=dict(x=e['bottom'][0],y=e['bottom'][1],z=-1),noViewpoint=True,zoom=1.5))
        pseudo=dict(rect=[48128,1280,256,256],lighting=[s|dict(x=48128+s['x'],y=1280+s['y']) for s in bunker['lighting']])
        b1=room_visit(pseudo,['kitchen'],'Final B1 kitchen and native night lighting',-1,True)
        b1['infected']=True;targets.append(b1)
        return targets
    targets=[room_visit(home,['kitchen'],'Cottage furnished kitchen'),
        room_visit(home,['bedroom'],'Cottage complete bed and facing'),
        room_visit(home,['livingroom'],'Cottage furnished living room'),
        room_visit(home,['kitchen'],'Cottage kitchen native night lighting',light=True),
        room_visit(mall,['departmentstore','grocery'],'Shopping centre sales floor'),
        room_visit(gun,['gunstore','policestorage'],'Gun shop sales and storage'),
        room_visit(tower,['office','livingroom','bedroom'],'Meridian top furnished room',tower['levels']-1),
        room_visit(tower,['office','livingroom','bedroom'],'Meridian tower native night lighting',0,True)]
    base=json.loads((ROOT/'build/test-urban-content.json').read_text())
    wanted={'Shopping centre parking apron','Meridian tower actual flight 1',
        'Meridian tower actual flight 12','Fortification first actual stair flight',
        'Fortification upper actual stair flight','Fortification crown and city skyline',
        'Public bunker entrance actual descent','B1 reception kitchen furnished wing',
        'B1 native room-light toggle','Meridian west gate inner court'}
    targets.extend(t for t in base if t['name'] in wanted)
    return targets


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'build/manifest.json')
    parser.add_argument('--native',type=Path,default=ROOT/'mod/common/media/maps/Meridian')
    parser.add_argument('--output',type=Path,default=ROOT/'build/test-urban-visual.json')
    parser.add_argument('--condensed',action='store_true')
    args=parser.parse_args()
    targets=prepare(json.loads(args.manifest.read_text(encoding='utf-8')),args.native,args.condensed)
    args.output.write_text(json.dumps(targets,indent=2),encoding='utf-8')
    print(f'{len(targets)} actual-room and physical-traversal targets: {args.output}')
