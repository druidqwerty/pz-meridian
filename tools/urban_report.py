"""Measured native urban inventory, separate from historical alpha.1 QA claims."""
from collections import Counter
import json


def write_report(root,manifest):
    records=[r for c in manifest['cells'] for r in c['records']]
    city=[r for r in records if r['site']=='Meridian']
    sites=[]
    for s in manifest['settlements']:
        if s['kind'] not in ('town','camp','lab','city','commercial'):continue
        rs=[r for r in records if r['site']==s['name']]
        sites.append(dict(name=s['name'],fraction=s['fraction'],kind=s['kind'],
            buildings=len(rs),types=dict(Counter(r['kind'] for r in rs)),
            floors=dict(sorted(Counter(r['levels'] for r in rs).items())),
            highrises6Plus=sum(r['levels']>=6 for r in rs)))
    report=dict(version=manifest['version'],surfaceStructures=len(records),
        rooms=sum(c['rooms'] for c in manifest['cells']),
        cityBuildings=len(city),cityHighrises6Plus=sum(r['levels']>=6 for r in city),
        tallestFloors=max(r['levels'] for r in records),
        roomLightCircuits=sum(c.get('roomLightCircuits',0) for c in manifest['cells']),
        visibleSurfaceSwitches=sum(l['kind']=='switch' for r in records for l in r.get('lighting',[])),
        shoppingCentres=sum(r['kind']=='bigboxmall' for r in records),
        gunshops=sum(r['kind']=='gunshop' for r in records),
        uniqueKindVariantPairs=len({(r['kind'],r.get('variant',0)) for r in records}),
        archetypeCounts=dict(Counter(r.get('archetype','unknown') for r in records)),
        silhouetteCounts=dict(Counter(r.get('silhouette','rect') for r in records)),
        wallPaletteCounts=dict(Counter(r.get('wallPalette','') for r in records)),
        parkZones=sum((c.get('streetscape') or {}).get('parks',0) for c in manifest['cells']),
        lotParkingLots=sum(((c.get('streetscape') or {}).get('publicRealm') or {}).get('lotParkingLots',0) for c in manifest['cells']),
        totalParkingSquares=sum(((c.get('streetscape') or {}).get('publicRealm') or {}).get('parkingSquares',0) for c in manifest['cells']),
        fortification=dict(depth=13,height=8,walkwayFloor=8,gateWidth=21,gateHeight=4),
        settlements=sites)
    assert report['cityHighrises6Plus']>=report['cityBuildings']//2
    assert report['shoppingCentres']==4 and report['gunshops']>=4
    assert report['visibleSurfaceSwitches']>=len(records)*3
    (root/'build/urban-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
