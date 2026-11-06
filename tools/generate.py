"""Compile original Meridian world deterministically into native B42 cells."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from time import monotonic
import argparse, hashlib, json
import numpy as np
from world import make_plan, progress, SAFE, ROUTE, SIZE, WAYPOINTS
from surface import raster, dress, city_wall
from map_binary import write_cell, audit_cell
from atlas import write_atlas
from landscape import landscape
from obstacles import dress_obstacles
from content_catalog import city_program
from story_scenes import convoy_trace
from expedition_decor import decorate as dress_expedition
from regional_program import settlement_program
from version import VERSION

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'mod/common/media/maps/Meridian'


def compile_cell(job):
    from architecture import build_structure, TILES
    from bunker import build_bunker
    from furnishing import EXTRAS, PALETTES
    from themed_rooms import PROPS
    from furniture_orientation import ALL_SPRITES
    from area_furnishing import world_reports
    from native_b42.activity_clusters import EXTRA_FACING
    cx,cy,features,site,bunker=job
    ground,tiles=raster(cx,cy,features)
    rooms,buildings,records=[],[],[]
    if site:
        iscity=site['kind']=='city'
        plans=settlement_program(site,cx,cy) if not iscity else None
        if iscity:
            district,plans=city_program(cx,cy)
        for i,plan in enumerate(plans):
            x,y,kind=plan['x'],plan['y'],plan['kind']
            # The wide enceinte owns the outer thirteen tiles; pull the last
            # perimeter row/column behind it without crossing the192avenue.
            if iscity and cx==191 and x==216:x=200
            if iscity and cy==7 and y==216:y=200
            if np.any(ground[y-2:y+36,x-2:x+36]==4):continue
            seed_val=plan.get('variant',(cx*37+cy*53+i*19)%100)
            rec=build_structure(tiles,rooms,buildings,x,y,kind,seed=seed_val)
            rec['rect']=[cx*256+rec['rect'][0],cy*256+rec['rect'][1],*rec['rect'][2:]]
            rec['spawn']=[cx*256+rec['spawn'][0],cy*256+rec['spawn'][1],rec['spawn'][2]]
            rec['site']=site['name'];rec['kind']=kind
            if iscity:rec['district']=district
            if site.get('chapter'):rec['chapter']=site['chapter']
            if rec.get('archiveDesk'):
                rec['archiveDesk'][0]+=cx*256;rec['archiveDesk'][1]+=cy*256
            for point in rec.get('caches',[]):point[0]+=cx*256;point[1]+=cy*256
            for point in rec.get('barricades',[]):point[0]+=cx*256;point[1]+=cy*256
            for light in rec.get('lighting',[]):
                light['x']+=cx*256;light['y']+=cy*256
            for flight in rec.get('stairTests',[]):
                for key in ('from','to'):
                    flight[key][0]+=cx*256;flight[key][1]+=cy*256
            world_reports(rec.get('furnishing',[]),cx,cy)
            records.append(rec)
            if kind=='fuel':
                # Actual vanilla pumps carry fuelAmount=20000, not decorative art.
                for dx in (3,9):
                    px,py=x+dx,y+rec['rect'][3]+6
                    if py<254:tiles[px,py,0]=['blends_street_01_86','location_shop_fossoil_01_14']
    dress(cx,cy,ground,tiles,bool(site))
    if site:
        site=dict(site)
        site['reserveShaft']=bool(bunker and (cx in (bunker['minCX'],bunker['maxCX']) or
            cy in (bunker['minCY'],bunker['maxCY'])))
    streets=landscape(tiles,ground,cx,cy,records,site) if site else None
    trace=convoy_trace(tiles,ground,cx,cy,records,site)
    expedition=dress_expedition(tiles,ground,cx,cy,records,site) if site else None
    roadside=dress_obstacles(cx,cy,ground,tiles,site)
    rampart=city_wall(cx,cy,tiles,rooms,buildings)
    under=None
    if bunker:
        under=build_bunker(tiles,rooms,buildings,cx,cy,bunker)
        world_reports(under.get('furnishing',[]),cx,cy)
        from bunker_wayfinding import decorate as bunker_wayfinding
        from building_signs import place_building_sign
        under['wayfinding']=bunker_wayfinding(tiles,cx,cy,under)
        if under.get('entrances'):
            under['wayfinding']['facadeSigns']=place_building_sign(tiles,(120,120,24,24),'bunker')
    safe=188<=cx<=191 and 4<=cy<=7
    density=[]
    for x in range(32):
        for y in range(32):
            land=(ground[y*8:y*8+8,x*8:x*8+8]!=1).mean()
            p=progress(cx*256+x*8,cy*256+y*8)
            value=round((1+24*p*p+(3 if site else 0))*land)
            density.append(0 if safe else value)
    stats=write_cell(OUT,cx,cy,tiles,rooms,buildings,density)
    # Every compiled cell is decoded and its exact tile ordering round-tripped.
    audit_cell(OUT,cx,cy,tiles)
    furnishing_names=set(TILES.values())|set(EXTRAS.values())|set(PROPS.values())|ALL_SPRITES|{s for values in PALETTES.values() for s in values}
    furnishing_names.update(sprite for variants in EXTRA_FACING.values() for sprite in variants.values())
    return dict(cell=[cx,cy],squares=stats['squares'],rooms=len(rooms),
                buildings=len(buildings),bytes=stats['bytes'],density=[min(density),max(density)],
                records=records,bunker=under,roadside=roadside,
                convoy=trace,expedition=expedition,cityWall=rampart,streetscape=streets,
                roomLightCircuits=sum(any(o[0]==7 for o in rr.get('objects',[])) for rr in rooms),
                furnitureInstances=sum(s in furnishing_names for names in tiles.values() for s in names),
                sprites=sorted({n for ns in tiles.values() for n in ns}))


def lua(value):
    if isinstance(value,dict):return '{'+','.join(str(k)+'='+lua(v) for k,v in value.items())+'}'
    if isinstance(value,list):return '{'+','.join(map(lua,value))+'}'
    if isinstance(value,str):return json.dumps(value,ensure_ascii=True)
    if isinstance(value,bool):return str(value).lower()
    return str(value)


def finish(cells,by_cell,sites,start):
    records=[r for c in cells for r in c['records']]
    spawn=next(r['spawn'] for r in records if r['site']=='Last Light' and r['kind']=='cottage')
    OUT.joinpath('spawnpoints.lua').write_text('function SpawnPoints()\nreturn {unemployed={'+
        f'{{posX={spawn[0]},posY={spawn[1]},posZ=0}}'+'}}\nend\n',encoding='utf-8')
    OUT.joinpath('map.info').write_text('title=Meridian: The Long Way Home\nfixed2x=true\n'+
        'description=An original southwest-to-northeast journey. Start at Last Light. New world only.\n'+
        f'zoomX={spawn[0]}\nzoomY={spawn[1]}\nzoomS=14.0\n',encoding='utf-8')
    OUT.joinpath('WorldGenOverride.lua').write_text('-- Native wilderness, authored roads only.\n'+
        'if worldgen then worldgen.roads = {} end\n',encoding='utf-8')
    config=dict(modId='MeridianLongWayHome',world=dict(minX=0,minY=0,maxX=SIZE-1,maxY=SIZE-1),
        safeCity=dict(x1=SAFE[0],y1=SAFE[1],x2=SAFE[2]-1,y2=SAFE[3]-1),
        starterVehicle=dict(x=640,y=48640,z=0,script='Base.SUV'),
        bunkers=[dict(id='continuity',x1=SAFE[0],y1=SAFE[1],x2=SAFE[2]-1,y2=SAFE[3]-1,minZ=-2,maxZ=-1)],
        storySites=[dict(id='site'+str(s['id']),x=s['x'],y=s['y'],z=0,textKey='UI_Meridian_Story'+str(s['id']+1)) for s in sites if s['id']<=12],
        caches=[dict(x=p[0],y=p[1],z=p[2]) for r in records for p in r.get('caches',[])])
    for c in cells:
        if c['bunker']:config['caches'].extend(c['bunker'].get('caches',[]))
        if c['bunker'] and not(188<=c['cell'][0]<=191 and 4<=c['cell'][1]<=7):
            x,y=c['cell'];config['bunkers'].append(dict(id=f'annex{x}_{y}',x1=x*256,y1=y*256,x2=x*256+255,y2=y*256+255,minZ=-2,maxZ=-1))
    for story in config['storySites']:
        s=next(s for s in sites if 'site'+str(s['id'])==story['id'])
        available=[r for r in records if r['site']==s['name']]
        if available:
            r=min(available,key=lambda r:(r['kind'] not in ('civic','lab','cottage'),
                (r['spawn'][0]-s['x'])**2+(r['spawn'][1]-s['y'])**2))
            story['x'],story['y'],story['z']=r['spawn']
    path=ROOT/'mod/42/media/lua/shared/Meridian/00_Config.lua'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('Meridian=Meridian or {}\nMeridian.Config='+lua(config)+'\n',encoding='utf-8')
    atlas=write_atlas(OUT,by_cell,records)
    manifest=dict(version=VERSION,map='Meridian',world=[0,0,SIZE-1,SIZE-1],
        safeCity=list(SAFE),road_tiles=ROUTE.length,route=WAYPOINTS,spawn=spawn,
        settlements=sites,cells=cells,atlas=atlas,seconds=round(monotonic()-start,1))
    (ROOT/'build/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    from expedition_guide import write_guide
    write_guide(ROOT,manifest)
    from urban_report import write_report
    write_report(ROOT,manifest)
    targets=[dict(name='Last Light',x=spawn[0],y=spawn[1],z=0,room=True)]
    for site_name in ('Stillwater','Station 6'):
        r=next(r for r in records if r['site']==site_name)
        targets.append(dict(name=r['site']+' '+r['kind'],x=r['spawn'][0],y=r['spawn'][1],z=0,room=True))
    targets += [dict(name='Meridian surface',x=48228,y=1124,z=0,safeSurface=True),
                dict(name='Continuity lobby',x=48256,y=1152,z=-1,room=True,infected=True),
                dict(name='Continuity deep hall',x=48512,y=1408,z=-2,room=True,infected=True),
                dict(name='Remote native forest',x=47000,y=45000,z=0)]
    (ROOT/'build/test-targets.json').write_text(json.dumps(targets,indent=2),encoding='utf-8')
    print(f'COMPLETE {len(cells)} cells / {len(records)} structures / {manifest["seconds"]}s',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();start=monotonic()
    _,by_cell,sites=make_plan()
    cell_sites={tuple(c):s for s in sites for c in s['cells']}
    bunkers={}
    for s in sites:
        if s['kind']=='lab':
            x,y=s['cells'][0];bunkers[x,y]=dict(minCX=x,maxCX=x,minCY=y,maxCY=y)
    for x in range(188,192):
        for y in range(4,8):bunkers[x,y]=dict(minCX=188,maxCX=191,minCY=4,maxCY=7)
    OUT.mkdir(parents=True,exist_ok=True);(ROOT/'build').mkdir(exist_ok=True)
    jobs=[(x,y,features,cell_sites.get((x,y)),bunkers.get((x,y))) for (x,y),features in sorted(by_cell.items())]
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(compile_cell,j) for j in jobs]
        for f in as_completed(futures):
            results.append(f.result())
            if len(results)%50==0:print(f'Compiled and decoded {len(results)}/{len(jobs)}',flush=True)
    finish(sorted(results,key=lambda c:c['cell']),by_cell,sites,start)


if __name__=='__main__':main()
