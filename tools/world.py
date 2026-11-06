"""Original Meridian geometry. Tile coordinates, not compressed geography."""
from math import sin, pi, hypot
from collections import defaultdict
from shapely.geometry import LineString, Point, box
from expedition import enrich_plan

SIZE = 49152
SAFE = (48128, 1024, 49152, 2048)
WAYPOINTS = [(512,48640),(14080,48640),(14080,39168),(3200,39168),
             (3200,29696),(28672,29696),(28672,20224),(23040,20224),
             (23040,10752),(40960,10752),(40960,1536),(48640,1536)]
ROUTE = LineString(WAYPOINTS)


def progress(x, y):
    return max(0, min(1, (x + SIZE - y) / (SIZE * 2)))


def make_plan():
    features = []
    def add(shape, material, prop=None):
        features.append((shape, material, prop))
    # Winding rivers and broad lakes are crossed by continuous raised causeways.
    for index, xbase in enumerate((9000, 21000, 36000)):
        line = LineString([(xbase + 1000*sin(y/4800+index),y)
                           for y in range(0,SIZE+256,256)])
        add(line.buffer(27+index*8), 'water', ('water','river'))
    for x,y,r in [(9400,42000,1100),(20700,26000,1600),(36500,6500,1400),
                  (5000,18000,900),(30000,36000,800)]:
        add(Point(x,y).buffer(r,quad_segs=20), 'water',('water','lake'))
    add(ROUTE.buffer(23,cap_style=2,join_style=2), 'verge')
    add(ROUTE.buffer(6,cap_style=2,join_style=2), 'road',('highway','primary'))
    # Civilian towns diminish; military installations become more frequent.
    settlements=[]
    specs=[(.000,'Last Light','town',3),(.065,'Alder Crossing','town',3),
           (.16,'Bellwether','town',2),(.26,'Stillwater','town',2),
           (.37,'Mercy Junction','town',2),(.47,'Northline','town',2),
           (.56,'Warden Pass','camp',2),(.64,'Station 6','lab',2),
           (.72,'White Relay','camp',2),(.79,'Hush Array','lab',2),
           (.85,'Gatehouse Nine','camp',2),(.92,'Continuity Annex','lab',2)]
    for i,(fraction,name,kind,n) in enumerate(specs):
        p=ROUTE.interpolate(fraction,normalized=True)
        cx,cy=int(p.x)//256,int(p.y)//256
        # Settlements occupy same-side plots, so the trunk remains traversable.
        cells=[(cx+dx,cy+dy) for dx in range(n) for dy in range(n)
               if 0<=cx+dx<192 and 0<=cy+dy<192]
        settlements.append(dict(id=i,name=name,kind=kind,cells=cells,
                                x=round(p.x),y=round(p.y),fraction=fraction))
        for a,b in cells:
            add(box(a*256,b*256,(a+1)*256,(b+1)*256),'town')
            for axis in (0,1):
                pts=[(a*256+128,b*256),(a*256+128,(b+1)*256)] if axis==0 else [
                    (a*256,b*256+128),((a+1)*256,b*256+128)]
                add(LineString(pts).buffer(4,cap_style=2),'road',('highway','residential'))
    settlements.append(dict(id=12,name='Meridian',kind='city',
        cells=[(x,y) for x in range(188,192) for y in range(4,8)],
        x=48640,y=1536,fraction=1))
    # Small logistical stations, not extra villages, support the full expedition.
    for distance in range(4500,int(ROUTE.length),4500):
        p=ROUTE.interpolate(distance);cx,cy=int(p.x)//256,int(p.y)//256
        if any((cx,cy) in s['cells'] for s in settlements):continue
        settlements.append(dict(id=100+distance//4500,name=f'Waystation {distance//4500:02}',
            kind='service',cells=[(cx,cy)],x=round(p.x),y=round(p.y),fraction=distance/ROUTE.length))
        add(box(cx*256,cy*256,(cx+1)*256,(cy+1)*256),'town')
        for pts in ([(cx*256+128,cy*256),(cx*256+128,(cy+1)*256)],
                    [(cx*256,cy*256+128),((cx+1)*256,cy*256+128)]):
            add(LineString(pts).buffer(4,cap_style=2),'road',('highway','service'))
    add(box(*SAFE),'town',('landuse','residential'))
    for x in range(188,192):
        for y in range(4,8):
            for off in (64,128,192):
                add(LineString([(x*256+off,y*256),(x*256+off,(y+1)*256)]).buffer(3),'road',('highway','residential'))
                add(LineString([(x*256,y*256+off),((x+1)*256,y*256+off)]).buffer(3),'road',('highway','residential'))
    # Final approach connects to the entire city's avenue network.
    add(ROUTE.buffer(6,cap_style=2,join_style=2),'road',('highway','primary'))
    # New content is static geography only; existing primary geometry and all
    # pre-existing settlement/shaft coordinates remain unchanged.
    enrich_plan(features,settlements,ROUTE,SIZE,SAFE)
    by_cell=defaultdict(list)
    for rec in features:
        a,b,c,d=rec[0].bounds
        for cx in range(max(0,int(a)//256),min(191,int(c)//256)+1):
            for cy in range(max(0,int(b)//256),min(191,int(d)//256)+1):
                if rec[0].intersects(box(cx*256,cy*256,(cx+1)*256,(cy+1)*256)):
                    by_cell[cx,cy].append(rec)
    return features,dict(by_cell),settlements
