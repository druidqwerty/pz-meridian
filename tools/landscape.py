"""Original vanilla-only Meridian public gardens and pedestrian streetscape.

Call after surface.dress and before bunkers. Does not modify ground/material
classification, authored buildings, roads, cell margins, or the shaft reserve.
"""
from random import Random
import numpy as np

PAVING='floors_exterior_tilesandstone_01_0'
ACCENT='floors_exterior_tilesandstone_01_1'
LAWN='blends_natural_01_48'
BENCH=('furniture_seating_outdoor_01_0','furniture_seating_outdoor_01_1')
LAMP='lighting_outdoor_01_0'
PLANTER='vegetation_indoor_01_8'
FLOWERS=('vegetation_groundcover_01_18','vegetation_groundcover_01_21')
TREES=('vegetation_trees_01_8','vegetation_trees_01_9','vegetation_trees_01_13')

def landscape(tiles,ground,cx,cy,records,site):
    """Decorate one cell in place; return deterministic diagnostic counts.

    Structure records may have local or absolute rects. Props have a four-tile
    road shoulder, two-tile facade setback, and leave every paved path clear.
    Garden benches are complete two-tile pairs. Native lamps contain their own
    B42 light properties; no Lua lighting loop or Viewpoint camera patch is used.
    """
    stats=dict(paving=0,trees=0,benches=0,planters=0,lamps=0)
    if not site:return stats
    city=site.get('kind')=='city'
    if not city and site.get('kind') not in ('town','service','expedition'):return stats
    rng=Random(cx*1000003+cy*104729+60013)
    hard=np.zeros((256,256),dtype=bool)
    setback=np.zeros_like(hard)
    paths=np.zeros_like(hard)
    road=np.asarray(ground)==4
    roadnear=np.zeros_like(hard)
    for dy in range(-4,5):
        for dx in range(-4,5):
            ya,yb=max(0,dy),min(256,256+dy)
            xa,xb=max(0,dx),min(256,256+dx)
            roadnear[ya:yb,xa:xb]|=road[ya-dy:yb-dy,xa-dx:xb-dx]
    local=[]
    for rec in records:
        x,y,w,h=rec['rect'];x=x-cx*256 if x>=256 else x;y=y-cy*256 if y>=256 else y
        if not (0<=x<256 and 0<=y<256):continue
        local.append((x,y,w,h))
        hard[max(0,y-1):min(256,y+h+2),max(0,x-1):min(256,x+w+2)]=True
        setback[max(0,y-3):min(256,y+h+5),max(0,x-3):min(256,x+w+4)]=True
    # All potential annex and city shaft sites are left untouched, even when
    # this particular cell has no shaft. Baseline geometry is shared with QA.
    hard[118:147,118:147]=True;setback[116:149,116:149]=True

    def bare(x,y,props=False):
        if not(6<=x<250 and 6<=y<250) or ground[y,x]==1 or road[y,x]:return False
        if hard[y,x] or (props and (setback[y,x] or roadnear[y,x] or paths[y,x])):return False
        names=tiles.get((x,y,0),[])
        return len(names)==1 and names[0].startswith(('blends_','floors_exterior_'))
    def pave(x,y,accent=False):
        if bare(x,y):
            tiles[x,y,0]=[ACCENT if accent else PAVING]
            paths[y,x]=True;stats['paving']+=1
    def prop(x,y,sprite,stat):
        if bare(x,y,True):
            tiles[x,y,0].append(sprite);stats[stat]+=1;return True
        return False
    # Two-wide curbs outline actual road geometry, including road crossings,
    # while the drivable original asphalt squares remain byte-for-byte intact.
    if city:
        for y in range(6,250):
            for x in range(6,250):
                if road[y,x]:continue
                near=road[max(0,y-2):min(256,y+3),max(0,x-2):min(256,x+3)]
                if near.any():pave(x,y)
    # Front-door approach connects to an existing nearby road by a short L.
    # Only floor-only exterior squares may be changed; it cannot eat walls.
    for x,y,w,h in local:
        sx,sy=x+w//2,y+h+3
        targets=[]
        for yy,xx in zip(*np.nonzero(road)):
            d=abs(int(xx)-sx)+abs(int(yy)-sy)
            if d<60:targets.append((d,int(xx),int(yy)))
        if targets:
            _,tx,ty=min(targets)
            # Prefer a horizontal first leg below the south facade. It remains
            # passable even when the nearest avenue is behind the building.
            for xx in range(min(sx,tx),max(sx,tx)+1):
                for off in (0,1):pave(xx,sy+off)
            for yy in range(min(sy,ty),max(sy,ty)+1):
                for off in (0,1):pave(tx+off,yy)
    # Sixteen little landscaped squares break the strict built grid into
    # planted blocks. Elsewhere, smaller roadside-town gardens are less formal.
    origins=[(x,y) for x in (8,72,136,200) for y in (8,72,136,200)]
    if not city:origins=origins[::5]
    for gx,gy in origins:
        if not all(bare(x,y) for x,y in ((gx,gy),(gx+12,gy+12))):continue
        for x in range(gx,gx+13):
            for y in range(gy,gy+13):
                if not bare(x,y):continue
                if x in (gx+5,gx+6) or y in (gy+5,gy+6):pave(x,y,accent=True)
                else:tiles[x,y,0]=[LAWN]
        for x,y in ((gx+2,gy+2),(gx+10,gy+2),(gx+2,gy+10),(gx+10,gy+10)):
            prop(x,y,rng.choice(TREES),'trees')
        # Seats face the clear central promenade, not its tree beds.
        bx,by=gx+1,gy+8
        if bare(bx,by,True) and bare(bx+1,by,True):
            tiles[bx,by,0].append(BENCH[0]);tiles[bx+1,by,0].append(BENCH[1]);stats['benches']+=1
        for x,y in ((gx+3,gy+3),(gx+9,gy+9)):
            if prop(x,y,PLANTER,'planters'):
                # Low flowers sit next to the planter, never in a walking lane.
                if bare(x+1,y,True):tiles[x+1,y,0].append(rng.choice(FLOWERS))
    if city:
        # Lamps and avenue trees are outside sidewalk/road clearance. A sparse
        # spacing prevents forests replacing a city's pedestrian streets.
        for off in (54,74,118,138,182,202):
            for along in (12,80,144,208):
                if (off+along+cx+cy)%3==0:prop(off,along,LAMP,'lamps')
                else:prop(off,along,rng.choice(TREES),'trees')
                if (off+along+cx+cy)%3==1:prop(along,off,LAMP,'lamps')
    return stats
