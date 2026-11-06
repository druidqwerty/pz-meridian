"""Role-specific vanilla furnishings; no extracted art or runtime spawning.

All names/properties checked against the owner's B42.21 *.tiles.txt. Tabletop
props share support squares; no disconnected multi-tile sofas or fake barricades.
"""
from random import Random

EXTRAS = dict(
 side='furniture_storage_01_52', lamp='lighting_indoor_02_0',
 radio='appliances_radio_01_0', tv='appliances_television_01_4',
 computer='appliances_com_01_72', phone='location_business_office_generic_02_16',
 microwave='appliances_cooking_01_28', coffee='appliances_cooking_01_56',
 plant='vegetation_indoor_01_12', flowers='vegetation_indoor_01_4',
 bin='trashcontainers_01_20', shower='fixtures_bathroom_01_32',
 medicine='fixtures_bathroom_01_28', crate='carpentry_02_104',
 metalcrate='constructedobjects_01_46', chest='furniture_storage_02_28',
 microscope='location_community_medical_01_136',
 bloodbag='location_community_medical_01_24',
 cart='location_community_medical_01_48',
 notices='location_community_medical_01_156',
)

PALETTES = dict(
 dresser=('furniture_storage_01_9','furniture_storage_01_12','furniture_storage_01_48'),
 chair=('furniture_seating_indoor_02_7','furniture_seating_indoor_02_0',
        'furniture_seating_indoor_03_4'),
 armchair=('furniture_seating_indoor_01_9','furniture_seating_indoor_01_12',
           'furniture_seating_indoor_02_44'),
 lowtable=('furniture_tables_low_01_18','furniture_tables_low_01_12',
           'furniture_tables_low_01_20'),
)


def palette(base, seed):
    result=dict(base)
    for i,(key,values) in enumerate(PALETTES.items()):
        result[key]=values[(seed+i)%len(values)]
    return result


def enrich(out,role,x,y,w,h,seed,base):
    """Densify walls/activity clusters while preserving side-door approach rims."""
    names=base | EXTRAS
    rng=Random(seed+x*17+y*31)

    def add(dx,dy,key,top=None):
        if not (1<=dx<w-1 and 0<=dy<h-1): return
        # Side-door paths and a continuous cross aisle are never furnishing sites.
        if dy in (h//2-1,h//2) and dx in (1,2,w-3,w-2): return
        p=x+dx,y+dy
        if p in out: return
        out[p]=[names[key]]
        if top: out[p].append(names[top])

    def top(dx,dy,key):
        if (x+dx,y+dy) in out: out[x+dx,y+dy].append(names[key])

    if role=='kitchen':
        for dx in range(4,w-2):
            add(dx,0,'counter', 'microwave' if dx==4 else 'coffee' if dx==5 else None)
        if w>=8 and h>=6:
            add(3,h-3,'table','flowers'); add(3,h-2,'chair')
        add(1,h-2,'bin')
    elif role=='bedroom':
        for dx in range(1,w-2,5):
            add(dx+1,0,'side','lamp' if dx==1 else 'radio')
        if w>=8: add(w-3,h-2,'shelves')
        add(1,h-2,'side','radio'); top(w-2,h-2,'flowers')
    elif role in ('hospitalroom','medical'):
        for dx in range(1,w-2,4):
            add(dx+1,0,'side'); add(dx+1,2,'bloodbag')
        if w>=9 and h>=7: add(w-3,h-2,'cart')
        top(w-2,h-2,'medicine'); add(1,h-2,'bin')
    elif role=='bathroom':
        if w>=6: add(3,0,'shower')
        top(w-2,0,'medicine'); add(1,h-2,'bin')
    elif role=='livingroom':
        add(w-3,0,'side','tv'); add(w-2,0,'plant')
        add(1,h-2,'side','lamp'); top(w-2,h-2,'radio')
        if w>=9 and h>=7:
            add(2,h-3,'desk','phone'); add(2,h-2,'chair')
    elif role in ('storage','armystorage','medicalstorage','policestorage'):
        crate='crate' if role=='storage' else 'metalcrate'
        for dx in range(2,w-2,3):
            add(dx,1,crate)
            if h>=9: add(dx,h-3,crate)
        if w>=9 and h>=8:
            add(w-3,0,'desk','radio'); add(w-3,1,'chair')
        add(1,h-2,'chest')
    elif role in ('laboratory','office','classroom'):
        for dx in range(1,w-2,4):
            top(dx,0,'microscope' if role=='laboratory' else
                'computer' if role=='office' else 'flowers')
        if w>=8: add(w-3,h-2,'shelves')
        add(1,h-2,'bin'); top(w-2,h-2,'phone' if role=='office' else 'radio')
        if h>=8: add(w-2,0,'plant')
    elif role in ('grocery','gasstore','library'):
        if h>=8:
            for dx in range(1,w-1,3): add(dx,3,'shelves')
        add(w-2,h-2,'desk','phone' if role=='library' else 'radio')
        add(1,h-3,'bin')
    elif role=='hall':
        # Used for the formerly empty large habitat halls, in separated bays.
        for dx in range(1,w-2,3): add(dx,0,'chair')
        add(w-2,0,'plant'); add(1,h-2,'side','radio')
        add(w-2,h-2,'shelves'); add(w-3,h-2,'bin')
        if w>=9 and h>=8:
            add(3,h-3,'table','flowers'); add(3,h-2,'chair')
    # Decor is intentionally on existing supports, not collision clutter.
    candidates=[p for p,v in out.items() if any(n in v for n in
        (base['desk'],base['counter'],base['dresser']))]
    if candidates and rng.random()<.55:
        out[rng.choice(candidates)].append(names['flowers'])


def lobby(put,tiles,x,y,w,h,z,base,seed):
    """Populate the wide lobby ends without touching axial hall or stair flight."""
    for dx,key in ((w-2,'plant'),(w-4,'chair')):
        put(tiles,x+dx,y+h-2,z,(base|EXTRAS)[key])
    put(tiles,x+w-6,y+h-2,z,base['side'])
    put(tiles,x+w-6,y+h-2,z,EXTRAS['radio' if seed%2 else 'flowers'])
    # Right alcove emergency furniture barricade; central route stays open.
    barricades=[]
    if seed%4 in (0,1):
        for dx,key in ((w-4,'crate'),(w-3,'metalcrate')):
            put(tiles,x+dx,y+h-4,z,EXTRAS[key])
            barricades.append([x+dx,y+h-4,z])
    return barricades
