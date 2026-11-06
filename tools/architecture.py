"""Original furnished Meridian buildings; only vanilla sprite *names* are used.

Native coordinates are local to a 256-tile cell. Entrances face south. The
unfurnished axial hall/lobby makes every named room and stair accessible.
"""
from random import Random
from furnishing import EXTRAS, furnish_room
from content_catalog import KINDS as CONTENT_KINDS, THEMES
from themed_rooms import furnish as furnish_themed
from story_scenes import archive_desk
from building_layouts import layout

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

def wall(tiles,x,y,z,direction,kind='solid',palette=16):
    offset = {'solid':0,'window':8,'door':10}[kind] + (direction == 'N')
    put(tiles,x,y,z,'walls_exterior_house_02_'+str(palette+offset))
    if kind != 'solid':
        sheet = 'fixtures_doors_01_' if kind == 'door' else 'fixtures_windows_01_'
        put(tiles,x,y,z,sheet+str(int(direction == 'N')))

def room_furniture(role,x,y,w,h,seed=0,blocked=()):
    """Verified facing and complete furniture grids, respecting actual doors."""
    yield from furnish_room(role,x,y,w,h,seed,base=TILES,blocked=blocked)


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
    """Create a function-specific building with native rooms, doors and stairs."""
    if kind not in KINDS: raise ValueError(f'Unknown structure kind: {kind}')
    w,h,levels,roles=KINDS[kind]
    if not(1<=x and x+w<255 and 1<=y and y+h+3<255):
        raise ValueError('Building requires an intact cell-local margin')
    rng=Random(seed); palette=rng.choice([0,16,32,48])
    if kind=='house' and seed%3==0: levels=2
    # Variation affects the actual skyline, never an unbounded random floor count.
    if kind in ('residentialtower','officetower'):levels+=seed%3-1
    indices=[];barricades=[];lighting=[];stair_tests=[]
    footprint=set()
    for z in range(levels):
        parts,doors,owners=layout(w,h,roles,kind,seed,z,levels)
        # Native room names and presentation themes remain separate.
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
        floor_rooms=[]
        for i,room in enumerate(parts):
            indices.append(len(rooms)); rr=dict(name=room['name'],level=z,
                rects=[(x+a,y+b,c,d) for a,b,c,d in room['rects']],objects=[])
            rooms.append(rr);floor_rooms.append(rr)
            floor=TILE if room['name'] not in ('bedroom','livingroom','hall') else WOOD
            for rx,ry,rw,rh in rr['rects']:
                for xx in range(rx,rx+rw):
                    for yy in range(ry,ry+rh): tiles[xx,yy,z]=[floor]
            if i or kind=='bigboxmall':
                for rx,ry,rw,rh in rr['rects']:
                    if i==0 and (rw<8 or rh<6):continue
                    for xx,yy,sprite in room_furniture(room.get('theme',room['name']),
                            rx,ry,rw,rh,seed+z*17+i,blocked=blocked):
                        put(tiles,xx,yy,z,sprite)
        # Derive the outside shell from the actual footprint, including courts
        # and setbacks; it is no longer always one rectangular bounding box.
        edges={}
        for dx,dy in owners:
            for ox,oy,direction in ((-1,0,'W'),(1,0,'W'),(0,-1,'N'),(0,1,'N')):
                if (dx+ox,dy+oy) not in owners:
                    edge=(max(dx,dx+ox),max(dy,dy+oy),direction)
                    edges[edge]='window' if ((dx if direction=='N' else dy)+seed)%4==2 else 'solid'
        edges[w//2,h,'N']='door' if z==0 else 'window'
        if z==0 and kind=='stripmall':
            # Each retail unit has its own public entrance onto a paved arcade.
            for room in parts[1:]:
                if room['name']!='grocery':continue
                a,b,c,d=room['rects'][0]
                edges[0,b+d//2,'W']='door'
        for (dx,dy,direction),style in edges.items():
            wall(tiles,x+dx,y+dy,z,direction,style,palette)
        if z==0 and kind in ('garage','firestation','depot'):
            # Verified native three-part metal garage door, not three singles.
            for dx,index in ((3,3),(4,4),(5,5)):
                names=tiles[x+dx,y,0]
                tiles[x+dx,y,0]=[n for n in names if not n.startswith(
                    ('walls_exterior_house_02_','fixtures_windows_01_','fixtures_doors_01_'))]
                put(tiles,x+dx,y,0,'walls_garage_01_'+str(index))
            for dx in range(2,7):
                for dy in range(max(-3,-y),0):tiles[x+dx,y+dy,0]=[PAVING]
        if z==0 and seed%3!=2:
            # Preserve ordinary native crowbar/hammer window barricades.
            planks=2+seed%3
            north=[(dx,dy) for (dx,dy,d),s in edges.items()
                   if d=='N' and s=='window' and dy==0
                   and 'fixtures_windows_01_1' in tiles.get((x+dx,y+dy,z),[])]
            for dx,dy in north[:2]:
                put(tiles,x+dx,y+dy,z,'carpentry_01_'+str(9+2*(planks-1)))
                barricades.append([x+dx,y+dy,z])
        for (dx,dy),i in owners.items():
            for ox,oy,d in [(-1,0,'W'),(0,-1,'N')]:
                if (dx+ox,dy+oy) in owners and owners[dx+ox,dy+oy]!=i:
                    wall(tiles,x+dx,y+dy,z,d,'door' if (dx,dy,d) in doors else 'solid',palette)
        if kind=='bigboxmall':
            # Complete native wall-sign grids over the fashion/sports units.
            for start,offset in ((2,24),((w-4)//4+2,20)):
                sheet='location_shop_accessories_genericsigns_01_' if offset==24 else 'location_shop_mall_signs_02_'
                for delta in range(4):put(tiles,x+start+delta,y+30,z,sheet+str(offset+delta))
        # Compact entrances get a side table/plant, not five tiles of empty lobby.
        if w>=16:
            put(tiles,x+w-2,y+h-1,z,TILES['plant'])
        if z>0:
            for dx in (2,3,4): tiles.pop((x+dx,y+h-3,z),None)
        if z<levels-1:
            for dx,idx in [(4,0),(3,1),(2,2)]: put(tiles,x+dx,y+h-3,z,'fixtures_stairs_01_'+str(idx))
            stair_tests.append({'from':[x+5,y+h-3,z],'to':[x+1,y+h-3,z+1]})
        from room_lighting import place_room_lighting
        for rr in floor_rooms:lighting.extend(place_room_lighting(tiles,rr,blocked=blocked))
        footprint.update(owners)
    for dx,dy in footprint:tiles[x+dx,y+dy,levels]=[ROOF]
    if kind=='stripmall':
        for dy in range(h+1):
            for dx in (-2,-1):
                if x+dx>=0:tiles[x+dx,y+dy,0]=[PAVING]
    # Sheltered entry apron gives each facade depth; no collision in the doorway.
    for xx in range(x+w//2-3,x+w//2+4):
        for yy in range(y+h+1,y+h+3): tiles[xx,yy,0]=[PAVING]
        for yy in range(y+h,y+h+3): put(tiles,xx,yy,1,ROOF)
    if seed%4 in (1,2) and kind not in ('house','cottage','ranch','guardhut','duplex','rowhouse'):
        # Moveable/scrappable shipping crates outside the facade, with an open
        # entrance apron and a walking route around both ends.
        for dx,key in ((2,'crate'),(3,'crate'),(4,'metalcrate')):
            tiles[x+dx,y+h+1,0]=[PAVING,TILES[key]]
            barricades.append([x+dx,y+h+1,0])
    caches=[]
    if seed%7==0:
        available=[(x+dx,y+dy,0) for dx,dy in sorted(footprint,reverse=True)
                   if (x+dx,y+dy) not in blocked and 1<dx<w-1 and 1<dy<h-2
                   and len(tiles.get((x+dx,y+dy,0),[]))==1]
        if available:
            cache=list(available[0]);tiles[tuple(cache)].append(TILES['metal']);caches.append(cache)
    buildings.append(indices)
    document=archive_desk(tiles,x,y,w,h,kind)
    return dict(kind=kind,rect=[x,y,w,h],levels=levels,spawn=[x+w//2,y+h-2,0],
                entrance=[x+w//2,y+h,0],cache=caches[0] if caches else None,
                caches=caches,barricades=barricades,archiveDesk=document,
                lighting=lighting,stairTests=stair_tests,layout=kind)
