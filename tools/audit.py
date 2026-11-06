"""Release gates independent of the builder: sprites, pairs, bounds and density."""
from pathlib import Path
import json,re,sys
from map_binary import _Reader
from collections import Counter
from version import VERSION

ROOT=Path(__file__).resolve().parents[1]
GAME=Path('G:/Steam/steamapps/common/ProjectZomboid')


def audit_furnishing(m):
    """Reject stale/truthy acceptance flags and independently check metrics."""
    assert m['version']==VERSION, 'Rebuild this version before auditing'
    furnishing=[r for c in m['cells']
        for owner in c['records']+([c['bunker']] if c.get('bunker') else [])
        for r in owner.get('furnishing',[])]
    assert furnishing, 'Missing actual room furnishing evidence'
    zoned=[r for r in furnishing if r['policy']=='zoned']
    assert zoned, 'No area-aware room plans'
    for r in furnishing:
        assert r['policy'] in ('zoned','compact','circulation'),r
        if r['policy']=='zoned':
            assert r['densityAudited'] is True and r['accepted'] is True and not r['warnings'],r
            assert r['connectedFloor'] is True and isinstance(r['groups'],list) and r['groups'],r
            assert r['floorSquares']==r['rect'][2]*r['rect'][3],r
            assert 0<r['furnishingSquares']<=r['floorSquares'],r
            assert r['occupiedSquares']==sum(g['footprint'] for g in r['groups']),r
            density=r['occupiedSquares']/r['furnishingSquares']
            assert r['targetDensity'][0]<=density<=r['targetDensity'][1],r
            assert r['largestEmptySquare']['side']<=r['maxEmptySide'],r
        else:
            assert r['accepted'] is None and r['densityAudited'] is False and r['reason'],r
    return furnishing,zoned


def main():
    m=json.loads((ROOT/'build/manifest.json').read_text())
    furnishing,zoned=audit_furnishing(m)
    folder=ROOT/'mod/common/media/maps/Meridian'
    defs=(GAME/'media/newtiledefinitions.tiles.txt').read_text()
    sprites=set(re.findall(r'// (\S+)\s+tile\s*\{',defs))
    unknown=set();rooms=0;buildings=0;safe=0;densities=[]
    for c in m['cells']:
        x,y=c['cell'];h=folder/f'{x}_{y}.lotheader';p=folder/f'world_{x}_{y}.lotpack'
        assert h.is_file() and p.is_file(),(x,y,'pair absent')
        r=_Reader(h.read_bytes());assert r.take(4)==b'LOTH' and r.uint()==1
        names=[r.line() for _ in range(r.count())];unknown.update(set(names)-sprites)
        density=h.read_bytes()[-1024:]
        if 188<=x<=191 and 4<=y<=7:
            assert max(density)==0,('safe city density',x,y);safe+=1
        rooms+=c['rooms'];buildings+=c['buildings']
        densities.append([x,y,min(density),max(density)])
    assert not unknown,sorted(unknown)
    assert safe==16
    assert len(list(folder.glob('*.lotheader')))==len(m['cells'])
    assert len(list(folder.glob('*.lotpack')))==len(m['cells'])
    # Actual first native saved-world META bounds were -250..250 inclusive.
    # Native B42 wilderness enlarges bounds beyond the authored 192-cell square.
    authored_part0=24+8*192*192+10*rooms+23*buildings
    part0=24+8*501*501+10*rooms+23*buildings
    assert part0<9000000
    assert 127000<m['road_tiles']<130000
    encounters=[e for c in m['cells'] for e in c.get('roadside',{}).get('encounters',[])]
    road_objects=[o for c in m['cells'] for o in c.get('roadside',{}).get('objects',[])]
    tunnel_objects=[o for c in m['cells'] if c.get('bunker') for o in c['bunker'].get('obstacles',[])]
    building_barricades=[p for c in m['cells'] for rec in c['records'] for p in rec.get('barricades',[])]
    assert encounters and road_objects and tunnel_objects and building_barricades,'Enrichment missing from compiled map'
    assert len({e['id'] for e in encounters})==len(encounters),'Duplicate encounter anchors'
    assert all(e['gapWidth']>=5 for e in encounters)
    content=json.loads((ROOT/'build/content-summary.json').read_text(encoding='utf-8'))
    assert content['counts']==dict(landmark=10,stop=12,base=7)
    assert len(content['habitatWings'])==16 and len(content['entrances'])==12
    assert len(content['convoyStages'])==7 and len(content['cityDistricts'])==4
    caches=[tuple(p) for c in m['cells'] for r in c['records'] for p in r.get('caches',[])]
    caches += [(p['x'],p['y'],p['z']) for c in m['cells'] if c.get('bunker') for p in c['bunker']['caches']]
    assert len(caches)==len(set(caches)), 'Duplicate supply lockers'
    assert len({(o['x'],o['y'],o['z']) for o in road_objects})==len(road_objects),'Overlapping road props'
    report=dict(version=VERSION,
        furnishing_reports=len(furnishing),
        furnishing_policies=dict(Counter(r['policy'] for r in furnishing)),
        zoned_programmes=dict(Counter(r['purpose'] for r in zoned)),
        all_zoned_rooms_accepted=True,
        native_pairs=len(m['cells']),rooms=rooms,buildings=buildings,
        native_bytes=sum(c['bytes'] for c in m['cells']),safe_zero_density_cells=safe,
        unknown_sprites=sorted(unknown),metadata_part0_bytes=part0,
        effective_native_cell_bounds=[-250,-250,250,250],
        authored_metadata_lower_bound_bytes=authored_part0,
        main_route_tiles=m['road_tiles'],road_encounters=len(encounters),
        road_salvage_objects=len(road_objects),tunnel_salvage_objects=len(tunnel_objects),
        building_barricade_squares=len(building_barricades),
        furniture_sprite_instances=sum(c.get('furnitureInstances',0) for c in m['cells']),
        content_counts=content['counts'],habitat_wings=16,entrance_roles=12,
        city_districts=content['cityDistricts'],convoy_stages=7,
        supply_lockers=len(caches),
        min_density=min(c[2] for c in densities),max_density=max(c[3] for c in densities))
    (ROOT/'build/static-audit.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
