"""Original furnished Meridian buildings; only vanilla sprite *names* are used.

Native coordinates are local to a 256-tile cell. Entrances face south. The
unfurnished axial hall/lobby makes every named room and stair accessible.
"""
from random import Random
from furnishing import EXTRAS, enrich, palette as furniture_palette, lobby
from content_catalog import KINDS as CONTENT_KINDS, THEMES
from themed_rooms import furnish as furnish_themed
from story_scenes import archive_desk

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
 'apartment': (28,24,3,('kitchen','bedroom','livingroom','bathroom')),
 'shop': (24,18,1,('grocery','storage','grocery','bathroom')),
 'fuel': (22,16,1,('gasstore','storage','office','bathroom')),
 'gas': (22,16,1,('gasstore','storage','office','bathroom')),
 'military': (30,24,1,('armystorage','bedroom','office','bathroom')),
 'barracks': (30,24,1,('bedroom','armystorage','bedroom','bathroom')),
 'lab': (30,26,2,('laboratory','medicalstorage','office','bathroom')),
 'hospital': (30,28,2,('hospitalroom','medicalstorage','medical','bathroom')),
 'clinic': (26,22,1,('medical','medicalstorage','office','bathroom')),
 'civic': (30,26,2,('library','office','office','bathroom')),
 'school': (30,26,2,('classroom','classroom','office','bathroom')),
 'warehouse': (30,24,1,('storage','storage','office','bathroom')),
 'police': (26,22,1,('policestorage','office','office','bathroom')),
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

def room_furniture(role,x,y,w,h,seed=0):
    """Yield complete furniture pairs and leave a generous clear door rim."""
    out = {}
    furnishing_tiles=furniture_palette(TILES,seed)
    def add(dx,dy,key):
        if 1 <= dx < w-1 and 0 <= dy < h-1:
            out[(x+dx,y+dy)] = [furnishing_tiles[key]]
    def sink(dx):
        add(dx,0,'counter')
        if (x+dx,y) in out: out[x+dx,y].append(furnishing_tiles['sink'])
    if role == 'kitchen':
        add(1,0,'fridge'); add(2,0,'oven'); sink(3)
        if w >= 7 and h >= 6:
            add(2,h-3,'table'); add(2,h-2,'chair')
    elif role in ('bedroom','hospitalroom','medical'):
        for dx in range(1,w-2,4 if role != 'bedroom' else 5):
            prefix = 'bed' if role == 'bedroom' else 'medical'
            add(dx,0,prefix+'_head'); add(dx,1,prefix+'_foot')
        add(w-2,h-2,'dresser' if role == 'bedroom' else 'metal')
        if role == 'medical': sink(w-2)
    elif role == 'bathroom':
        add(1,0,'toilet'); sink(w-2)
    elif role == 'livingroom':
        add(1,0,'armchair'); add(3,0,'armchair'); add(2,0,'lowtable')
        add(w-2,h-2,'shelves')
    elif role in ('storage','armystorage','medicalstorage','policestorage'):
        for dx in range(1,w-1,3):
            add(dx,0,'metal')
            if h >= 7: add(dx,h-2,'metal')
    elif role in ('laboratory','office','classroom'):
        for dx in range(1,w-2,4):
            add(dx,0,'counter' if role == 'laboratory' else 'desk')
            add(dx,1,'chair')
            if role == 'classroom' and h >= 8:
                add(dx,4,'desk'); add(dx,5,'chair')
        add(w-2,h-2,'files' if role == 'office' else 'metal')
        if role == 'laboratory': sink(w-2)
    elif role in ('grocery','gasstore','library'):
        for dx in range(1,w-1,3):
            add(dx,0,'shelves')
            if h >= 8: add(dx,h-3,'shelves')
        if role != 'library': add(1,h-2,'fridge')
    enrich(out,role,x,y,w,h,seed,furnishing_tiles)
    furnish_themed(out,role,x,y,w,h,furnishing_tiles)
    for (xx,yy),sprites in out.items():
        for sprite in sprites: yield xx,yy,sprite

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
    """Create one original building and return local bounds/spawn/cache metadata."""
    if kind not in KINDS: raise ValueError(f'Unknown structure kind: {kind}')
    w,h,levels,roles=KINDS[kind]
    if not(1<=x and x+w<255 and 1<=y and y+h+3<255):
        raise ValueError('Building requires an intact cell-local margin')
    rng=Random(seed); palette=rng.choice([0,16,32,48]) if kind in ('house','cottage','apartment') else 16
    if kind=='house' and seed%3==0: levels=2
    parts,doors=plan(w,h,roles); owners={}; indices=[]; barricades=[]
    for i,room in enumerate(parts):
        for rx,ry,rw,rh in room['rects']:
            for xx in range(rx,rx+rw):
                for yy in range(ry,ry+rh): owners[xx,yy]=i
    for z in range(levels):
        for i,room in enumerate(parts):
            indices.append(len(rooms)); rr=dict(name=room['name'],level=z,
                rects=[(x+a,y+b,c,d) for a,b,c,d in room['rects']],objects=[])
            rooms.append(rr)
            floor=TILE if room['name'] not in ('bedroom','livingroom','hall') else WOOD
            for rx,ry,rw,rh in rr['rects']:
                for xx in range(rx,rx+rw):
                    for yy in range(ry,ry+rh): tiles[xx,yy,z]=[floor]
            if i:
                for rx,ry,rw,rh in rr['rects']:
                    role=THEMES.get(kind,roles)[i-1]
                    for xx,yy,sprite in room_furniture(role,rx,ry,rw,rh,seed+z*17+i): put(tiles,xx,yy,z,sprite)
        barricades.extend(lobby(put,tiles,x,y,w,h,z,TILES,seed+z))
        for xx in range(x,x+w):
            for yy in (y,y+h):
                k='door' if yy==y+h and xx==x+w//2 and z==0 else ('window' if (xx-x)%5==2 else 'solid')
                wall(tiles,xx,yy,z,'N',k,palette)
        for yy in range(y,y+h):
            for xx in (x,x+w): wall(tiles,xx,yy,z,'W','window' if (yy-y)%5==2 else 'solid',palette)
        # Vanilla MOBarricade replaces these authored frames with IsoBarricade.
        # Never seal the entrance or the internal circulation doors.
        if z==0 and seed%3!=2:
            planks=2+seed%3
            for xx,yy,index in ((x+2,y,9+2*(planks-1)),
                                (x+7,y+h-1,1+2*(planks-1))):
                put(tiles,xx,yy,z,'carpentry_01_'+str(index))
                barricades.append([xx,yy,z])
        for (dx,dy),i in owners.items():
            for ox,oy,d in [(-1,0,'W'),(0,-1,'N')]:
                if owners.get((dx+ox,dy+oy),i)!=i:
                    wall(tiles,x+dx,y+dy,z,d,'door' if (dx,dy,d) in doors else 'solid',palette)
        if z>0:
            for dx in (2,3,4): tiles.pop((x+dx,y+h-3,z),None)
        if z<levels-1:
            for dx,idx in [(4,0),(3,1),(2,2)]: put(tiles,x+dx,y+h-3,z,'fixtures_stairs_01_'+str(idx))
        put(tiles,x+w//2,y+h-1,z,'lighting_indoor_01_3')
    for xx in range(x,x+w):
        for yy in range(y,y+h): tiles[xx,yy,levels]=[ROOF]
    # Sheltered entry apron gives each facade depth; no collision in the doorway.
    for xx in range(x+w//2-3,x+w//2+4):
        for yy in range(y+h+1,y+h+3): tiles[xx,yy,0]=[PAVING]
        for yy in range(y+h,y+h+3): put(tiles,xx,yy,1,ROOF)
    if seed%4 in (1,2):
        # Moveable/scrappable shipping crates outside the facade, with an open
        # entrance apron and a walking route around both ends.
        for dx,key in ((2,'crate'),(3,'crate'),(4,'metalcrate')):
            tiles[x+dx,y+h+1,0]=[PAVING,TILES[key]]
            barricades.append([x+dx,y+h+1,0])
    caches=[]
    if seed%7==0:
        cache=[x+w-2,y+2,0]
        tiles[tuple(cache)]=[TILE,TILES['metal']]
        caches.append(cache)
    buildings.append(indices)
    document=archive_desk(tiles,x,y,w,h,kind)
    return dict(kind=kind,rect=[x,y,w,h],levels=levels,spawn=[x+w//2,y+h-2,0],
                entrance=[x+w//2,y+h,0],cache=caches[0] if caches else None,
                caches=caches,barricades=barricades,archiveDesk=document)
