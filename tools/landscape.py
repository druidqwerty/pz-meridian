"""Original vanilla-only Meridian public gardens and pedestrian streetscape.

Call after surface.dress and before bunkers. Does not modify ground/material
classification, authored buildings, roads, cell margins, or the shaft reserve.
"""
from random import Random
import numpy as np
from public_geometry import dilate, exterior_path
from public_realm import public_realm, clear_exterior

PAVING='floors_exterior_tilesandstone_01_0'
ACCENT='floors_exterior_tilesandstone_01_1'
LAWN='blends_natural_01_48'
BENCH=('furniture_seating_outdoor_01_0','furniture_seating_outdoor_01_1')
LAMP='lighting_outdoor_01_0'
PLANTER='vegetation_indoor_01_8'
# These flowers are actually registered in B42.21, not merely listed in the
# text sidecar (groundcover18/21 exist there but fail native CellLoader lookup).
FLOWERS=('vegetation_indoor_01_4','vegetation_indoor_01_12')
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
    rng=Random(cx*1000003+cy*104729+60013)
    hard=np.zeros((256,256),dtype=bool)
    setback=np.zeros_like(hard)
    paths=np.zeros_like(hard)
    road=np.asarray(ground)==4
    roadnear=dilate(road,4)
    local=[]
    for rec in records:
        x,y,w,h=rec['rect'];x=x-cx*256 if x>=256 else x;y=y-cy*256 if y>=256 else y
        if not (0<=x<256 and 0<=y<256):continue
        local.append((x,y,w,h))
        hard[max(0,y-1):min(256,y+h+2),max(0,x-1):min(256,x+w+2)]=True
        setback[max(0,y-3):min(256,y+h+5),max(0,x-3):min(256,x+w+4)]=True
    # All potential annex and city shaft sites are left untouched, even when
    # this particular cell has no shaft. Baseline geometry is shared with QA.
    shaft=site.get('reserveShaft',city and (cx in (188,191) or cy in (4,7)))
    if shaft:
        hard[118:147,118:147]=True;setback[116:149,116:149]=True

    def bare(x,y,props=False):
        if not(0<=x<256 and 0<=y<256) or ground[y,x]==1 or road[y,x]:return False
        if hard[y,x] or (props and (setback[y,x] or roadnear[y,x] or paths[y,x])):return False
        names=tiles.get((x,y,0),[])
        return clear_exterior(names) if not props else len(names)==1 and clear_exterior(names)
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
    sidewalks=dilate(road,2)&~road
    for y,x in zip(*np.nonzero(sidewalks)):pave(int(x),int(y))
    realm,realm_mask=public_realm(tiles,ground,cx,cy,records,site,hard)
    paths|=realm_mask
    stats['publicRealm']=realm
    # Front-door approach connects to an existing nearby road by a short L.
    # Only floor-only exterior squares may be changed; it cannot eat walls.
    obstacles=hard|(ground==1)
    for (xx,yy,zz),names in tiles.items():
        if zz==0 and not clear_exterior(names) and not road[yy,xx]:
            obstacles[yy,xx]=True
    targets=road|paths
    for x,y,w,h in local:
        sx,sy=x+w//2,y+h+3
        path=exterior_path((sx,sy),targets,obstacles,limit=120)
        if path:
            for xx,yy in path:
                for dx,dy in ((0,0),(1,0),(0,1)):pave(xx+dx,yy+dy)
            targets|=paths
        else:
            stats.setdefault('unconnectedApproaches',[]).append([sx,sy])
    # Sixteen little landscaped squares break the strict built grid into
    # planted blocks. Elsewhere, smaller roadside-town gardens are less formal.
    origins=[(x,y) for x in (8,72,136,200) for y in (8,72,136,200)]
    if not city:origins=origins[::5]
    for gx,gy in origins:
        if paths[gy:gy+13,gx:gx+13].any():continue
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
