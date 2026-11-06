"""Original vanilla-only Meridian public gardens, neighborhood parks and streetscape.

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
FLOWERS=('vegetation_indoor_01_4','vegetation_indoor_01_12',
         'vegetation_ornamental_01_16','vegetation_ornamental_01_17',
         'vegetation_ornamental_01_18','vegetation_ornamental_01_19')
HEDGE_W='vegetation_ornamental_01_0'
HEDGE_N='vegetation_ornamental_01_1'
PATIO_CHAIR='furniture_seating_outdoor_01_16'
PARK_BIN='trashcontainers_01_20'
TREES=('vegetation_trees_01_8','vegetation_trees_01_9','vegetation_trees_01_13')
RESIDENTIAL_KINDS={'cottage','house','ranch','duplex','rowhouse','farm'}


def landscape(tiles,ground,cx,cy,records,site):
    """Decorate one cell in place; return deterministic diagnostic counts."""
    stats=dict(paving=0,trees=0,benches=0,planters=0,lamps=0,parks=0,flowerbeds=0)
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
        local.append((x,y,w,h,rec.get('kind','')))
        hard[max(0,y-1):min(256,y+h+2),max(0,x-1):min(256,x+w+2)]=True
        setback[max(0,y-3):min(256,y+h+5),max(0,x-3):min(256,x+w+4)]=True
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

    sidewalks=dilate(road,2)&~road
    for y,x in zip(*np.nonzero(sidewalks)):pave(int(x),int(y))
    realm,realm_mask=public_realm(tiles,ground,cx,cy,records,site,hard)
    paths|=realm_mask
    stats['publicRealm']=realm

    obstacles=hard|(ground==1)
    for (xx,yy,zz),names in tiles.items():
        if zz==0 and not clear_exterior(names) and not road[yy,xx]:
            obstacles[yy,xx]=True
    targets=road|paths
    for x,y,w,h,_ in local:
        sx,sy=x+w//2,y+h+3
        path=exterior_path((sx,sy),targets,obstacles,limit=120)
        if path:
            for xx,yy in path:
                for dx,dy in ((0,0),(1,0),(0,1)):pave(xx+dx,yy+dy)
            targets|=paths
        else:
            stats.setdefault('unconnectedApproaches',[]).append([sx,sy])

    # 1. Pocket parks and landscaped corner squares.
    origins=[(x,y) for x in (8,72,136,200) for y in (8,72,136,200)]
    if not city and not records:origins=origins[::5]
    for gx,gy in origins:
        if paths[gy:gy+13,gx:gx+13].any():continue
        if not all(bare(x,y) for x,y in ((gx,gy),(gx+12,gy+12))):continue
        stats['parks']+=1
        for x in range(gx,gx+13):
            for y in range(gy,gy+13):
                if not bare(x,y):continue
                if x in (gx+5,gx+6) or y in (gy+5,gy+6):pave(x,y,accent=True)
                else:tiles[x,y,0]=[LAWN]
        for x,y in ((gx+2,gy+2),(gx+10,gy+2),(gx+2,gy+10),(gx+10,gy+10)):
            prop(x,y,rng.choice(TREES),'trees')
        bx,by=gx+1,gy+8
        if bare(bx,by,True) and bare(bx+1,by,True):
            tiles[bx,by,0].append(BENCH[0]);tiles[bx+1,by,0].append(BENCH[1]);stats['benches']+=1
        for x,y in ((gx+3,gy+3),(gx+9,gy+9)):
            if prop(x,y,PLANTER,'planters'):
                if bare(x+1,y,True):
                    tiles[x+1,y,0].append(rng.choice(FLOWERS));stats['flowerbeds']+=1
        prop(gx+8,gy+4,LAMP,'lamps')

    # 2. Full-block neighborhood parks on open town/city plots and residential garden yards.
    if records:
        for bx in (24,88,152,216):
            for by in (24,88,152,216):
                pw,ph=24,20
                if bx+pw>=248 or by+ph>=248:continue
                if hard[by:by+ph,bx:bx+pw].any() or paths[by:by+ph,bx:bx+pw].any() or roadnear[by:by+ph,bx:bx+pw].any():
                    continue
                if not all(bare(bx+dx,by+dy) for dx in (0,pw-1) for dy in (0,ph-1)):
                    continue
                stats['parks']+=1
                mx,my=bx+pw//2,by+ph//2
                for xx in range(bx,bx+pw):
                    for yy in range(by,by+ph):
                        if not bare(xx,yy):continue
                        if abs(xx-mx)<=1 or abs(yy-my)<=1 or (abs(xx-mx)<=3 and abs(yy-my)<=3):
                            pave(xx,yy,accent=True)
                        else:
                            tiles[xx,yy,0]=[LAWN]
                for xx in range(bx+2,bx+pw-2,2):
                    if abs(xx-mx)>2:
                        prop(xx,by,HEDGE_N,'planters')
                for yy in range(by+2,by+ph-2,2):
                    if abs(yy-my)>2:
                        prop(bx,yy,HEDGE_W,'planters')
                for tx,ty in ((bx+3,by+3),(bx+pw-4,by+3),(bx+3,by+ph-4),(bx+pw-4,by+ph-4)):
                    prop(tx,ty,rng.choice(TREES),'trees')
                for fx,fy in ((bx+5,by+4),(bx+pw-6,by+4),(bx+5,by+ph-5),(bx+pw-6,by+ph-5)):
                    prop(fx,fy,rng.choice(FLOWERS),'flowerbeds')
                for bx0,by0 in ((mx-5,my-3),(mx+3,my+3)):
                    if bare(bx0,by0,True) and bare(bx0+1,by0,True):
                        tiles[bx0,by0,0].append(BENCH[0]);tiles[bx0+1,by0,0].append(BENCH[1]);stats['benches']+=1
                prop(mx-4,my+2,LAMP,'lamps')
                prop(mx+4,my-2,PARK_BIN,'planters')

        for x,y,w,h,kind in local:
            if kind not in RESIDENTIAL_KINDS:continue
            gx,gy,gw,gh=x+w+2,y+2,12,min(12,h-2)
            if gx+gw>=244 or gy+gh>=244 or gh<8:continue
            if hard[gy:gy+gh,gx:gx+gw].any() or paths[gy:gy+gh,gx:gx+gw].any() or roadnear[gy:gy+gh,gx:gx+gw].any():
                continue
            stats['parks']+=1
            for xx in range(gx,gx+gw):
                for yy in range(gy,gy+gh):
                    if bare(xx,yy):tiles[xx,yy,0]=[LAWN]
            prop(gx+3,gy+2,rng.choice(TREES),'trees')
            prop(gx+gw-3,gy+gh-3,rng.choice(FLOWERS),'flowerbeds')
            prop(gx+2,gy+gh-3,PATIO_CHAIR,'benches')

    if city:
        for off in (54,74,118,138,182,202):
            for along in (12,80,144,208):
                if (off+along+cx+cy)%3==0:prop(off,along,LAMP,'lamps')
                else:prop(off,along,rng.choice(TREES),'trees')
                if (off+along+cx+cy)%3==1:prop(along,off,LAMP,'lamps')
    return stats
