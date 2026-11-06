"""Static expedition geography; no Lua, quests, inventory or power systems."""
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from expedition_sites import CHAPTERS, POIS, STOPS, BASES, chapter_at, compound_layout


def _road(features, points, category='service', width=3):
    line=LineString(points)
    if line.length == 0:
        return
    features.append((line.buffer(width+6,cap_style=2,join_style=2),'verge',None))
    features.append((line.buffer(width,cap_style=2,join_style=2),'road',('highway',category)))


def _available_cell(route, fraction, used, water, size):
    """Select a fully dry independent compound with a perpendicular road arm."""
    origin=route.interpolate(fraction,normalized=True)
    before=route.interpolate(max(0,route.length*fraction-16))
    after=route.interpolate(min(route.length,route.length*fraction+16))
    horizontal=abs(after.x-before.x)>abs(after.y-before.y)
    choices=[]
    for along in (0,-256,256,-512,512,-768,768,-1024,1024):
        for away in (384,-384,640,-640,896,-896,1152,-1152):
            px=origin.x+(along if horizontal else away)
            py=origin.y+(away if horizontal else along)
            cx,cy=int(px)//256,int(py)//256
            if (cx,cy) in used or not(0<=cx<size//256 and 0<=cy<size//256):
                continue
            parcel=box(cx*256,cy*256,(cx+1)*256,(cy+1)*256)
            center=Point(cx*256+128,cy*256+128)
            nearest=route.interpolate(route.project(center))
            if abs(nearest.x-center.x)>0.01 and abs(nearest.y-center.y)>0.01:
                continue
            arm=LineString([nearest,center])
            if arm.length>1400 or route.distance(parcel)<28:
                continue
            if water.intersects(parcel) or water.intersects(arm.buffer(10)):
                continue
            choices.append((center.distance(origin),cx,cy,nearest,center))
    if not choices:
        raise ValueError(f'No dry connected expedition parcel at route fraction {fraction}')
    return min(choices,key=lambda item:item[:3])


def _loops(features, route, water, size):
    """Short parallel detours reconnect locally; no cross-region shortcuts."""
    loops=[]
    for chapter in CHAPTERS[:-1]:
        fraction=(chapter[3]+chapter[4])/2
        for shift in (0,256,-256,512,-512):
            distance=route.length*fraction+shift
            a,b=route.interpolate(distance-512),route.interpolate(distance+512)
            if abs(a.x-b.x)>1 and abs(a.y-b.y)>1:
                continue
            horizontal=abs(a.x-b.x)>abs(a.y-b.y)
            for side in (384,-384,640,-640):
                dx,dy=(0,side) if horizontal else (side,0)
                points=[(a.x,a.y),(a.x+dx,a.y+dy),(b.x+dx,b.y+dy),(b.x,b.y)]
                line=LineString(points)
                if not box(16,16,size-16,size-16).covers(line.buffer(12)):
                    continue
                if water.intersects(line.buffer(12)):
                    continue
                _road(features,points,'secondary',4)
                loops.append(dict(chapter=chapter[0],kind='regional',points=points,
                                  mainSpan=1024,length=line.length))
                break
            if loops and loops[-1]['chapter']==chapter[0]:
                break
        if not loops or loops[-1]['chapter']!=chapter[0]:
            raise ValueError(f'No dry regional detour in chapter {chapter[0]}')
    return loops


def enrich_plan(features, sites, route, size, safe):
    """Mutate existing feature/site lists; preserve their public tuple contract."""
    water=unary_union([shape for shape,material,_ in features if material=='water'])
    used={tuple(cell) for site in sites for cell in site['cells']}
    loops=_loops(features,route,water,size)
    for site in sites:
        site['chapter']=chapter_at(min(site['fraction'],1))
    briefs=[]
    for fraction,key,name,ru,kinds,description in POIS:
        briefs.append((fraction,key,name,ru,kinds,description,'landmark'))
    for fraction,key,name,ru,kinds in STOPS:
        briefs.append((fraction,key,name,ru,kinds,'Roadside stop using ordinary native rooms.','stop'))
    for fraction,key,name,ru,kinds,description in BASES:
        briefs.append((fraction,key,name,ru,kinds,description,'base'))
    for index,brief in enumerate(briefs):
        fraction,key,name,ru,kinds,description,category=brief
        _,cx,cy,nearest,center=_available_cell(route,fraction,used,water,size)
        used.add((cx,cy))
        site=dict(id=201+index,name=name,nameRU=ru,kind='expedition',archetype=key,
                  cells=[(cx,cy)],x=round(center.x),y=round(center.y),fraction=fraction,
                  chapter=chapter_at(fraction),category=category,description=description,
                  structures=compound_layout(key,kinds),connector=[(nearest.x,nearest.y),(center.x,center.y)])
        sites.append(site)
        parcel=box(cx*256,cy*256,(cx+1)*256,(cy+1)*256)
        if key=='sluice-seven':
            # Authored impoundment below a flat native embankment. It meets the
            # parcel edge, so the raster polygon has no unsupported inner ring.
            reservoir=box(cx*256+24,cy*256+176,cx*256+232,cy*256+320)
            features.append((reservoir,'water',('water','lake')))
            parcel=parcel.difference(reservoir)
            site['reservoir']=[cx*256+24,cy*256+176,cx*256+232,cy*256+320]
        features.append((parcel,'town',('landuse','commercial')))
        _road(features,site['connector'])
        for points in ([(cx*256+128,cy*256),(cx*256+128,(cy+1)*256)],
                       [(cx*256,cy*256+128),((cx+1)*256,cy*256+128)]):
            _road(features,points)
        # A local second exit provides a service loop around each compound.
        # It meets the same principal road no more than256tiles away.
        horizontal=abs(nearest.x-center.x)<0.01
        dx,dy=(256,0) if horizontal else (0,256)
        endpoint=Point(nearest.x+dx,nearest.y+dy)
        line=LineString([center,(center.x+dx,center.y+dy),endpoint])
        if (box(16,16,size-16,size-16).covers(line.buffer(10)) and
                route.distance(endpoint)<0.01 and not water.intersects(line.buffer(10))):
            points=list(line.coords)
            _road(features,points)
            site['secondExit']=points
    city=next(site for site in sites if site['kind']=='city')
    city['expeditionBase']=dict(id='meridian-home',name='Meridian Expedition Home',
                               nameRU='Экспедиционный дом Meridian',chapter='meridian')
    return dict(chapters=[dict(id=c[0],name=c[1],nameRU=c[2],start=c[3],end=c[4]) for c in CHAPTERS],
                regionalLoops=loops,landmarks=10,stops=12,bases=7)
