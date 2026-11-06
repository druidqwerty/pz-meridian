"""Original furnished Meridian buildings; only vanilla sprite *names* are used.

Native coordinates are local to a 256-tile cell. Entrances face south. The
unfurnished axial hall/lobby makes every named room and stair accessible.
"""
from furnishing import EXTRAS, furnish_room
from content_catalog import KINDS as CONTENT_KINDS, THEMES
from themed_rooms import furnish as furnish_themed
from story_scenes import archive_desk
from building_layouts import layout
from building_variants import variant_spec
from exterior_compounds import dress_building_exterior

WOOD = 'floors_interior_tilesandwood_01_40'
TILE = 'floors_interior_tilesandwood_01_16'
ROOF = 'roofs_01_22'
PAVING = 'floors_exterior_tilesandstone_01_0'
TILES = dict(fridge='appliances_refrigeration_01_0', oven='appliances_cooking_01_0',
 counter='fixtures_counters_01_0', sink='fixtures_sinks_01_0',
 toilet='fixtures_bathroom_01_4', dresser='furniture_storage_01_9',
 shelves='furniture_shelving_01_40', metal='furniture_storage_02_0',
 desk='location_community_school_01_5', files='location_business_office_generic_01_16',
 table='furniture_tables_high_01_4', chair='furniture_seating_indoor_02_7',
 armchair='furniture_seating_indoor_01_9', lowtable='furniture_tables_low_01_18',
 bed_head='furniture_bedding_01_9', bed_foot='furniture_bedding_01_8',
 medical_head='location_community_medical_01_17', medical_foot='location_community_medical_01_16')
TILES.update(EXTRAS)
KINDS = {
 'house': (18,16,1,('kitchen','bedroom','livingroom','bathroom')),
 'cottage': (16,14,1,('kitchen','bedroom','livingroom','bathroom')),
 'apartment': (28,30,4,('kitchen','bedroom','livingroom','bathroom')),
 'shop': (24,18,1,('grocery','storage','grocery','bathroom')),
 'fuel': (22,16,1,('gasstore','storage','office','bathroom')),
 'gas': (22,16,1,('gasstore','storage','office','bathroom')),
 'military': (30,24,1,('armystorage','bedroom','office','bathroom')),
 'barracks': (30,24,1,('bedroom','armystorage','bedroom','bathroom')),
 'lab': (30,26,2,('laboratory','medicalstorage','office','bathroom')),
 'hospital': (30,28,2,('hospitalroom','medicalstorage','medical','bathroom')),
 'clinic': (26,22,1,('medical','medicalstorage','office','bathroom')),
 'civic': (32,30,3,('library','office','office','bathroom')),
 'school': (34,32,2,('classroom','classroom','office','bathroom')),
 'warehouse': (34,26,1,('storage','storage','office','bathroom')),
 'police': (28,26,2,('policestorage','office','office','bathroom')),
}
KINDS.update(CONTENT_KINDS)


def put(tiles,x,y,z,sprite):
    if not (0 <= x < 256 and 0 <= y < 256):
        raise ValueError(f'Architecture outside native cell: {x},{y}')
    tiles.setdefault((x,y,z),[]).append(sprite)


def wall(tiles,x,y,z,direction,kind='solid',palette=16,*,
         sheet='walls_exterior_house_02',win=('fixtures_windows_01',0),
         door=('fixtures_doors_01',0)):
    offset = {'solid':0,'window':8,'door':10}[kind] + (direction == 'N')
    put(tiles,x,y,z,f'{sheet}_{palette+offset}')
    if kind == 'window':
        put(tiles,x,y,z,f'{win[0]}_{win[1]+int(direction == "N")}')
    elif kind == 'door':
        put(tiles,x,y,z,f'{door[0]}_{door[1]+int(direction == "N")}')


def room_furniture(role,x,y,w,h,seed=0,blocked=(),**kwargs):
    """Verified facing and complete furniture grids, respecting actual doors."""
    yield from furnish_room(role,x,y,w,h,seed,base=TILES,blocked=blocked,**kwargs)


def plan(w,h,roles):
    left,split,lobby = (w-3)//2,(h-5)//2,h-5
    rects = [(0,0,left,split),(left+3,0,w-left-3,split),
             (0,split,left,lobby-split),(left+3,split,w-left-3,lobby-split)]
    rooms=[dict(name='hall',rects=[(left,0,3,lobby),(0,lobby,w,5)])]
    doors=[]
    for i,(role,rect) in enumerate(zip(roles,rects)):
        rooms.append(dict(name=role,rects=[rect]))
        rx,ry,rw,rh=rect
        doors.append((left if i%2==0 else left+3,ry+rh//2,'W'))
    return rooms,set(doors)


def build_structure(tiles,rooms,buildings,x,y,kind,seed=0):
    """Create a function-specific building with 100 variant traits per kind."""
    if kind not in KINDS: raise ValueError(f'Unknown structure kind: {kind}')
    w,h,levels,roles=KINDS[kind]
    if not(1<=x and x+w<255 and 1<=y and y+h+3<255):
        raise ValueError('Building requires an intact cell-local margin')
    spec=variant_spec(kind,seed)
    vid=spec['variant_id']
    if kind=='house' and seed%3==0: levels=2
    if kind in ('residentialtower','officetower'):levels+=seed%3-1
    indices=[];barricades=[];lighting=[];stair_tests=[];furnishing=[];caches=[]
    cache_point=None
    owners_by_z={}
    for z in range(levels):
        ext_sheet,ext_base=spec['wall'] if z==0 else spec['upper_wall']
        int_sheet,int_base=spec['interior_wall']
        win_spec=spec['window']
        ext_door=spec['ext_door']
        int_door=spec['int_door']
        parts,doors,owners=layout(w,h,roles,kind,seed,z,levels)
        owners_by_z[z]=set(owners)
        themes=THEMES.get(kind)
        if themes and len(parts)==5:
            for i,room in enumerate(parts[1:]):room['theme']=themes[i]
        blocked={(x+w//2,y+h-2),(x+w//2,y+h-1)}
        if kind in ('garage','firestation','depot'):
            blocked|={(x+dx,y+dy) for dx in range(2,7) for dy in range(0,6)}
        if levels>1:
            blocked|={(x+dx,y+h-3+dy) for dx in range(1,7) for dy in (-1,0,1)}
        for dx,dy,direction in doors:
            if direction=='W':
                blocked|={(x+dx+a,y+dy) for a in (-1,0,1)}
            else:
                blocked|={(x+dx,y+dy+b) for b in (-1,0,1)}
        if kind=='bigboxmall':
            blocked|={(x+dx,y+dy) for dx in range(w) for dy in (32,33)}
            blocked|={(x+dx,y+dy) for dx in (w//2-1,w//2) for dy in range(h)}
        if z==0 and seed%7==0:
            candidates=[(dx,dy) for (dx,dy),owner in sorted(owners.items(),reverse=True)
                if owner and (x+dx,y+dy) not in blocked
                and (x+dx,y+dy+1) not in blocked
                and all(owners.get((dx+ox,dy+oy))==owner
                        for ox,oy in ((-1,0),(1,0),(0,-1),(0,1)))]
            if candidates:
                dx,dy=candidates[0];cache_point=(x+dx,y+dy)
                blocked.add((x+dx,y+dy+1))
        floor_rooms=[]
        fl=spec['floors']
        for i,room in enumerate(parts):
            indices.append(len(rooms)); rr=dict(name=room['name'],level=z,
                rects=[(x+a,y+b,c,d) for a,b,c,d in room['rects']],objects=[])
            rooms.append(rr);floor_rooms.append(rr)
            rname=room['name']
            floor=(fl['hall'] if rname=='hall' else fl['wet'] if rname in ('bathroom','kitchen','medical','laboratory')
                   else fl['secondary'] if rname=='bedroom' else fl['primary'])
            for rx,ry,rw,rh in rr['rects']:
                for xx in range(rx,rx+rw):
                    for yy in range(ry,ry+rh): tiles[xx,yy,z]=[floor]
            if i or kind=='bigboxmall':
                for rx,ry,rw,rh in rr['rects']:
                    if i==0 and (rw<8 or rh<6):continue
                    role=room.get('theme',room['name'])
                    programme = ('restaurantkitchen' if role=='kitchen' and
                        kind in ('bigboxmall','diner') else 'dining' if
                        role=='assembly' and kind in ('bigboxmall','diner') else
                        'dormitory' if role=='bedroom' and kind in
                        ('military','barracks','firestation') else role)
                    for xx,yy,sprite in room_furniture(role,
                            rx,ry,rw,rh,seed+z*17+i,blocked=blocked,
                            programme=programme,reports=furnishing,z=z,
                            loot_role=room['name'],
                            obstacles=(cache_point,) if z==0 and cache_point else ()):
                        put(tiles,xx,yy,z,sprite)
        edges={}
        period=spec['window_period']
        wmod=spec['window_mod']
        for dx,dy in owners:
            for ox,oy,direction in ((-1,0,'W'),(1,0,'W'),(0,-1,'N'),(0,1,'N')):
                if (dx+ox,dy+oy) not in owners:
                    edge=(max(dx,dx+ox),max(dy,dy+oy),direction)
                    pos=dx if direction=='N' else dy
                    edges[edge]='window' if (pos+vid)%period==wmod else 'solid'
        edges[w//2,h,'N']='door' if z==0 else 'window'
        if z==0 and kind=='stripmall':
            for room in parts[1:]:
                if room['name']!='grocery':continue
                a,b,c,d=room['rects'][0]
                edges[0,b+d//2,'W']='door'
        for (dx,dy,direction),style in edges.items():
            use_door=('fixtures_doors_01',0) if (kind=='stripmall' and dx==0 and direction=='W') else ext_door
            wall(tiles,x+dx,y+dy,z,direction,style,ext_base,
                 sheet=ext_sheet,win=win_spec,door=use_door)
        if z==0 and kind in ('garage','firestation','depot'):
            for dx,index in ((3,3),(4,4),(5,5)):
                names=tiles[x+dx,y,0]
                tiles[x+dx,y,0]=[n for n in names if not n.startswith(
                    ('walls_','fixtures_windows_','fixtures_doors_'))]
                put(tiles,x+dx,y,0,'walls_garage_01_'+str(index))
            for dx in range(2,7):
                for dy in range(max(-3,-y),0):tiles[x+dx,y+dy,0]=[PAVING]
        if z==0 and seed%3!=2:
            planks=2+seed%3
            north=[(dx,dy) for (dx,dy,d),s in edges.items()
                   if d=='N' and s=='window' and dy==0
                   and any(n.startswith('fixtures_windows_') and int(n.rsplit('_',1)[1])%2==1
                           for n in tiles.get((x+dx,y+dy,z),[]))]
            for dx,dy in north[:2]:
                put(tiles,x+dx,y+dy,z,'carpentry_01_'+str(9+2*(planks-1)))
                barricades.append([x+dx,y+dy,z])
        for (dx,dy),i in owners.items():
            for ox,oy,d in [(-1,0,'W'),(0,-1,'N')]:
                if (dx+ox,dy+oy) in owners and owners[dx+ox,dy+oy]!=i:
                    wall(tiles,x+dx,y+dy,z,d,'door' if (dx,dy,d) in doors else 'solid',
                         int_base,sheet=int_sheet,win=win_spec,door=int_door)
        if kind=='bigboxmall':
            for start,offset in ((2,24),((w-4)//4+2,20)):
                sheet='location_shop_accessories_genericsigns_01_' if offset==24 else 'location_shop_mall_signs_02_'
                for delta in range(4):put(tiles,x+start+delta,y+30,z,sheet+str(offset+delta))
        if w>=16:
            put(tiles,x+w-2,y+h-1,z,TILES['plant'])
        if z>0:
            for dx in (2,3,4): tiles.pop((x+dx,y+h-3,z),None)
        if z<levels-1:
            for dx,idx in [(4,0),(3,1),(2,2)]: put(tiles,x+dx,y+h-3,z,'fixtures_stairs_01_'+str(idx))
            stair_tests.append({'from':[x+5,y+h-3,z],'to':[x+1,y+h-3,z+1]})
        from room_lighting import place_room_lighting
        for rr in floor_rooms:lighting.extend(place_room_lighting(tiles,rr,blocked=blocked))
    for z in range(levels):
        exposed=owners_by_z[z]-owners_by_z.get(z+1,set())
        for dx,dy in exposed:
            names=tiles.setdefault((x+dx,y+dy,z+1),[])
            if ROOF not in names:names.insert(0,ROOF)
            if spec['roof']!=ROOF and spec['roof'] not in names:
                names.insert(1,spec['roof'])
    dress_building_exterior(tiles,x,y,w,h,kind,spec,owners_by_z[0])
    if kind=='stripmall':
        for dx in (-2,-1):
            for dy in range(h+3):tiles[x+dx,y+dy,0]=[PAVING]
    for dx in range(-1,2):
        for dy in (0,1,2): tiles[x+w//2+dx,y+h+dy,0]=[PAVING]
    archive=archive_desk(tiles,x,y,w,h,kind)
    if cache_point:
        put(tiles,cache_point[0],cache_point[1],0,TILES['metal'])
        caches.append([cache_point[0],cache_point[1],0])
    buildings.append(indices)
    return dict(rect=[x,y,w,h],spawn=[x+w//2,y+h-2,0],rooms=len(indices),levels=levels,
        variant=vid,archetype=spec['archetype'],silhouette=spec['silhouette'],
        wallPalette=f"{spec['wall'][0]}_{spec['wall'][1]}",
        caches=caches,archiveDesk=archive,barricades=barricades,
        lighting=lighting,stairTests=stair_tests,furnishing=furnishing)
