"""Ordinary-life habitat scenes using verified, complete vanilla furnishings."""
from furnishing import EXTRAS

PROPS = dict(EXTRAS, washer='appliances_laundry_01_4',
             dryer='appliances_laundry_01_12', basket='appliances_laundry_01_24',
             tools='location_business_machinery_01_32',
             grinder='construction_01_6')
THEMED = {'laundry','shower','workshop','pump','electrical','communications',
          'archive','nursery','gym','assembly'}


def furnish(out,role,x,y,w,h,base):
    if role not in THEMED: return
    names = base | PROPS
    def add(dx,dy,key,top=None):
        if not(1<=dx<w-1 and 0<=dy<h-1): return
        # Room doors are on the side midpoints. Keep their approach clear.
        if dy in (h//2-1,h//2) and dx in (1,2,w-3,w-2): return
        p=x+dx,y+dy
        if p in out:return
        out[p]=[names[key]]
        if top:out[p].append(names[top])
    if role=='laundry':
        for i,dx in enumerate(range(1,w-1,2)):
            add(dx,0,'washer' if i%2==0 else 'dryer')
            add(dx,h-2,'basket')
        add(w-2,h-3,'counter')
    elif role=='shower':
        for dx in range(1,w-1,2):
            add(dx,0,'shower'); add(dx,h-2,'metal')
    elif role in ('workshop','pump','electrical'):
        for i,dx in enumerate(range(1,w-1,3)):
            add(dx,0,'tools' if role=='workshop' else 'metal')
            add(dx,h-2,'counter',None if role=='workshop' else 'radio')
            if role=='workshop':add(dx,1,'grinder')
        if role=='pump':
            for dx in range(2,w-2,3):add(dx,1,'sink')
        add(1,h-3,'crate'); add(w-2,h-3,'bin')
    elif role in ('communications','archive'):
        for dx in range(1,w-1,3):
            add(dx,0,'files' if role=='archive' else 'desk',
                None if role=='archive' else 'radio')
            add(dx,h-2,'shelves' if role=='archive' else 'desk',
                None if role=='archive' else 'computer')
        add(w-2,1,'metal'); add(1,1,'chair')
    elif role=='nursery':
        for dx in range(1,w-2,3):
            add(dx,0,'lowtable','flowers'); add(dx,1,'chair')
            add(dx,h-2,'shelves')
        add(w-2,0,'chest'); add(w-2,h-2,'plant')
    elif role=='gym':
        # Open exercise floor, changing lockers, seating and equipment chests.
        for dx in range(1,w-1,2):
            add(dx,0,'metal'); add(dx,h-2,'chair')
        add(1,h-3,'chest'); add(w-2,h-3,'chest')
    elif role=='assembly':
        for dx in range(1,w-2,2):
            add(dx,0,'chair'); add(dx,h-2,'chair')
        add(w-2,0,'desk','radio');add(w-2,h-2,'plant')
