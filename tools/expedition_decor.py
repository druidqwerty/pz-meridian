"""Native compound set dressing with explicit road/door/building clearance."""
import numpy as np

PAVING='floors_exterior_tilesandstone_01_0'
DIRT='blends_natural_01_32'
CRATE='carpentry_01_16'
PALLET='construction_01_4'
GRINDER='construction_01_6'
LOCKER='furniture_storage_02_0'
LAMP='lighting_outdoor_01_0'
TREE='vegetation_trees_01_8'
BENCH=('furniture_seating_outdoor_01_0','furniture_seating_outdoor_01_1')
ALL_SPRITES=(PAVING,DIRT,CRATE,PALLET,GRINDER,LOCKER,LAMP,TREE,*BENCH)


def decorate(tiles,ground,cx,cy,records,site):
    """Dress distinct authored yards; never overwrite structures or roads.

    Rows describe actual objects rather than new gameplay. Crates, lockers,
    workstations and roadwork supplies use the ordinary game actions/loot.
    """
    stats=dict(archetype=site.get('archetype'),props=0,paved=0,types=[])
    if site.get('kind')!='expedition':
        return stats
    blocked=np.zeros((256,256),dtype=bool)
    road=ground==4
    for dy in range(-3,4):
        for dx in range(-3,4):
            ya,yb=max(0,dy),min(256,256+dy)
            xa,xb=max(0,dx),min(256,256+dx)
            blocked[ya:yb,xa:xb]|=road[ya-dy:yb-dy,xa-dx:xb-dx]
    for rec in records:
        x,y,w,h=rec['rect']
        if x>=256:x-=cx*256
        if y>=256:y-=cy*256
        blocked[max(0,y-3):min(256,y+h+7),max(0,x-3):min(256,x+w+4)]=True
    def bare(x,y):
        return (6<=x<250 and 6<=y<250 and not blocked[y,x] and
                ground[y,x]!=1 and len(tiles.get((x,y,0),[]))==1)
    def pave(x,y,sprite=PAVING):
        if bare(x,y):
            tiles[x,y,0]=[sprite];stats['paved']+=1
    def prop(x,y,sprite):
        if bare(x,y):
            tiles[x,y,0].append(sprite);stats['props']+=1
            if sprite not in stats['types']:stats['types'].append(sprite)
            return True
        return False
    def yard(x1,y1,x2,y2,sprite=PAVING):
        for x in range(x1,x2):
            for y in range(y1,y2):pave(x,y,sprite)
    def rows(x1,y1,x2,y2,sprite,step=4):
        for x in range(x1,x2,step):
            for y in range(y1,y2,step):prop(x,y,sprite)
    def garden(x1,y1,x2,y2):
        for x in range(x1,x2,16):
            for y in range(y1,y2,16):
                prop(x,y,TREE)
                if bare(x+3,y+4) and bare(x+4,y+4):
                    prop(x+3,y+4,BENCH[0]);prop(x+4,y+4,BENCH[1])
        for y in range(y1,y2):
            for x in range((x1+x2)//2,(x1+x2)//2+2):pave(x,y)
    key=site['archetype']
    if key=='sluice-seven':
        yard(16,156,240,176)
        rows(24,160,232,161,LAMP,24)
        rows(32,84,112,112,GRINDER,20)
        rows(160,84,232,112,PALLET,12)
        stats['setpiece']='impoundment_and_flat_embankment'
    elif key=='dead-letter':
        yard(156,16,240,112);yard(16,160,112,240)
        rows(168,24,232,96,CRATE,8);rows(24,168,104,224,LOCKER,12)
        stats['setpiece']='sorting_loading_aprons'
    elif key=='test-block':
        yard(16,108,112,116);yard(160,56,240,64)
        rows(160,80,240,112,LOCKER,16)
        rows(24,176,112,224,CRATE,24)
        stats['setpiece']='identical_houses_observation_supply_yard'
    elif key=='still-pines':
        garden(64,160,112,240);garden(160,80,240,112)
        rows(176,216,240,240,LOCKER,16)
        stats['setpiece']='treatment_park_and_closed_wing_supplies'
    elif key=='evacuation':
        yard(16,64,112,112);yard(160,104,240,116)
        rows(24,72,112,112,CRATE,16);rows(160,72,232,96,PALLET,12)
        rows(64,176,112,240,PALLET,16)
        stats['setpiece']='unfinished_boarding_queues_and_materials'
    elif key=='regional-archive':
        garden(160,24,240,112);yard(64,176,112,240)
        rows(72,184,112,232,LOCKER,10)
        stats['setpiece']='reading_courtyard_and_records_loading'
    elif key=='relay':
        yard(160,72,240,112);yard(24,216,112,240)
        rows(168,80,232,104,LOCKER,12);rows(24,224,112,240,GRINDER,20)
        stats['setpiece']='communications_equipment_yard'
    elif key=='quarry':
        yard(16,64,112,112,DIRT);yard(64,160,112,240,DIRT)
        rows(24,72,112,104,PALLET,8);rows(72,168,104,232,GRINDER,16)
        stats['setpiece']='material_terraces_and_repair_yard'
    elif key=='water-intake':
        yard(64,64,112,112);yard(160,216,240,240)
        rows(72,72,112,104,GRINDER,12);rows(168,224,232,240,PALLET,16)
        stats['setpiece']='utility_equipment_and_service_apron'
    elif key=='regional-museum':
        garden(16,160,112,240);yard(160,72,240,112)
        rows(168,80,232,104,GRINDER,20)
        stats['setpiece']='public_garden_and_maintenance_exhibits'
    elif key in ('farmstead','vet'):
        yard(24,152,112,240,DIRT)
        rows(32,160,104,232,CRATE,16);garden(160,152,240,240)
        stats['setpiece']='rural_storage_and_farmyard'
    elif key in ('camp','rest','forest-station','visitor','chapel'):
        garden(24,152,112,240);garden(160,152,240,240)
        rows(24,88,112,112,CRATE,24)
        stats['setpiece']='sheltered_native_picnic_and_supply_yard'
    else:
        yard(24,152,112,240);rows(32,160,104,224,CRATE,16)
        yard(160,152,240,240);rows(168,160,232,224,PALLET,20)
        rows(24,88,112,112,LAMP,24)
        stats['setpiece']='service_and_overnight_aprons'
    # Repeat physical material motifs at road approaches, not just chapter
    # labels in metadata. Existing native objects remain normally interactive.
    signatures={
        'last-light':(LAMP,CRATE), 'farmland':(TREE,CRATE),
        'industry':(PALLET,GRINDER), 'reservoir':(LAMP,TREE),
        'forest':(TREE,TREE), 'restricted':(LOCKER,PALLET),
        'meridian':(LAMP,LOCKER),
    }
    signature=signatures[site['chapter']]
    for x,y in ((144,12),(144,240),(12,144),(240,144)):
        for offset,sprite in enumerate(signature):prop(x+offset*3,y,sprite)
    stats['chapterMotif']=site['chapter']
    return stats
