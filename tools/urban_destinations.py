"""Dedicated large retail/service parcels, not giant buildings forced into house lots."""
from shapely.geometry import box,LineString
from shapely.ops import unary_union
from expedition import _available_cell,_road
from expedition_sites import chapter_at


def add_destinations(features,sites,route,size):
    used={tuple(c) for s in sites for c in s['cells']}
    water=unary_union([g for g,m,_ in features if m=='water'])
    programmes=(
        (.105,'Valley Regional Shopping Centre','Торговый центр долины'),
        (.355,'Foundry Retail Park','Торговый парк «Литейный»'),
        (.505,'Lakeside Shopping Centre','Приозёрный торговый центр'),
        (.935,'Continuity Supply Galleria','Торговая галерея Continuity'),
    )
    for i,(fraction,name,ru) in enumerate(programmes):
        _,cx,cy,nearest,center=_available_cell(route,fraction,used,water,size)
        used.add((cx,cy));x0,y0=cx*256,cy*256
        structures=[dict(x=24,y=24,kind='bigboxmall'),
                    dict(x=168,y=24,kind='gunshop'),dict(x=168,y=72,kind='diner')]
        site=dict(id=401+i,name=name,nameRU=ru,kind='commercial',
            cells=[(cx,cy)],x=int(center.x),y=int(center.y),fraction=fraction,
            chapter=chapter_at(fraction),structures=structures,
            parking=[[16,120,224,104]],plazas=[[24,100,96,16]],
            connector=[(nearest.x,nearest.y),(center.x,center.y)])
        sites.append(site)
        features.append((box(x0,y0,x0+256,y0+256),'town',('landuse','retail')))
        # The access arm enters a wide open parking aisle at the cell centre.
        # Its internal branch bends south, never through the retail anchor.
        _road(features,[nearest,center],'service',4)
        _road(features,[(center.x,center.y),(center.x,y0+232),
                        (x0+16,y0+232),(x0+240,y0+232)],'service',4)
