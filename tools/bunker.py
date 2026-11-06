"""Original two-level continuity habitat, linked across native-cell boundaries.

Six-wide axial galleries join all cells. Residential, medical, military and
laboratory wings have real rooms, vanilla furniture and physical doors/stairs.
"""
from architecture import put,wall,room_furniture,TILE,ROOF,PAVING,TILES

def rects_for(points):
    """Merge horizontal runs vertically; disjoint native RoomRect coverage."""
    rows={}
    for x,y in points: rows.setdefault(y,[]).append(x)
    active={}; result=[]
    for y in range(256):
        xs=sorted(rows.get(y,[])); runs=[]
        for x in xs:
            if runs and runs[-1][0]+runs[-1][1]==x: runs[-1][1]+=1
            else: runs.append([x,1])
        current={}
        for x,w in runs:
            key=x,w
            if key in active:
                rx,ry,rw,rh=active.pop(key); current[key]=(rx,ry,rw,rh+1)
            else: current[key]=(x,y,w,1)
        result.extend(active.values()); active=current
    result.extend(active.values())
    return result

def build_bunker(tiles,rooms,buildings,cx,cy,config):
    loX,hiX,loY,hiY=[config[k] for k in ('minCX','maxCX','minCY','maxCY')]
    if not(loX<=cx<=hiX and loY<=cy<=hiY): return dict(entrances=[],caches=[])
    shaft=(cx in (loX,hiX) and cy in (loY,hiY))
    entrances=[]; caches=[]; indices=[]; total_area=0
    roles=('bedroom','kitchen','hospitalroom','armystorage','laboratory','medicalstorage')
    for z in (-2,-1):
        owner={}; specs=[dict(name='hall',role='hall')]; doors=set()
        def fill(x,y,w,h,i=0):
            for xx in range(x,x+w):
                for yy in range(y,y+h): owner[xx,yy]=i
        fill(0,126,256,6); fill(126,0,6,256); fill(120,120,24,24)
        for q,(qx,qy) in enumerate(((16,16),(144,16),(16,144),(144,144))):
            fill(16 if qx==16 else 132,qy+40,116 if qx==16 else 108,16)
            big=(cx+cy+q+z)%5==0
            if big:
                i=len(specs); role='hall' if z==-1 else 'laboratory'
                specs.append(dict(name=role,role=role,rect=(qx,qy,96,96)))
                fill(qx,qy,96,96,i)
                doors.add((qx+96 if qx==16 else qx,qy+48,'W'))
            else:
                for row in range(2):
                    for col in range(3):
                        rx,ry=qx+col*32,qy+row*56
                        role=roles[(cx*3+cy+q+col+row+(0 if z==-1 else 3))%len(roles)]
                        i=len(specs); specs.append(dict(name=role,role=role,rect=(rx,ry,28,40)))
                        fill(rx,ry,28,40,i)
                        doors.add((rx+14,ry+40 if row==0 else ry,'N'))
        total_area+=len(owner)
        for i,spec in enumerate(specs):
            points={p for p,n in owner.items() if n==i}
            if not points: continue
            indices.append(len(rooms)); rooms.append(dict(name=spec['name'],level=z,
                rects=rects_for(points),objects=[]))
            for xx,yy in points: tiles[xx,yy,z]=[TILE]
            if spec['role']=='hall': continue
            x,y,w,h=spec['rect']
            # Furnished bays, not a single line of props in an empty mega-room.
            for bx in range(x,x+w-6,14):
                for by in range(y,y+h-6,12):
                    for xx,yy,sprite in room_furniture(spec['role'],bx,by,min(12,x+w-bx),min(10,y+h-by)):
                        put(tiles,xx,yy,z,sprite)
            if (cx+cy+i+z)%9==0:
                caches.append(dict(x=cx*256+x+w-2,y=cy*256+y+2,z=z,kind=spec['name']))
                put(tiles,x+w-2,y+2,z,TILES['metal'])
        # Emit canonical N/W boundary edges once. Internal galleries remain open
        # at shared cell boundaries; the final outer boundary is sealed.
        for (x,y),i in owner.items():
            for dx,dy,d in ((-1,0,'W'),(0,-1,'N')):
                other=owner.get((x+dx,y+dy))
                seam=(d=='W' and x==0 and cx>loX and 126<=y<132) or (d=='N' and y==0 and cy>loY and 126<=x<132)
                if other!=i and not seam:
                    wall(tiles,x,y,z,d,'door' if (x,y,d) in doors else 'solid',0)
            for dx,dy,d in ((1,0,'W'),(0,1,'N')):
                xx,yy=x+dx,y+dy
                if (xx,yy) in owner: continue
                seam=(xx==256 and cx<hiX and 126<=y<132) or (yy==256 and cy<hiY and 126<=x<132)
                if seam: continue
                xx,yy=min(xx,255),min(yy,255)
                wall(tiles,xx,yy,z,d,'door' if (xx,yy,d) in doors else 'solid',0)
        # Electrical light switches reference genuine B42 room metaobjects.
        for room in rooms:
            if room['level']==z and room['rects']:
                rx,ry,rw,rh=room['rects'][0]
                if rw>=3 and rh>=3: put(tiles,rx+1,ry,z,'lighting_indoor_01_0')
    # Stairs -2 -> -1. Landing is west of the top, bottom approach east.
    for x,idx in ((130,0),(129,1),(128,2)):
        put(tiles,x,136,-2,'fixtures_stairs_01_'+str(idx)); tiles.pop((x,136,-1),None)
    if shaft:
        # Architectural entrance is a guarded masonry pavilion, not a teleport.
        ix=[]
        for z in (0,):
            ix.append(len(rooms)); rooms.append(dict(name='hall',level=z,rects=[(120,120,24,24)],objects=[]))
            for x in range(120,144):
                for y in range(120,144): tiles[x,y,z]=[PAVING]
            for x in range(120,144):
                wall(tiles,x,120,z,'N','window' if x%6==2 else 'solid',0)
                wall(tiles,x,144,z,'N','door' if x in (131,132) else 'solid',0)
            for y in range(120,144):
                for x in (120,144): wall(tiles,x,y,z,'W','window' if y%6==2 else 'solid',0)
            for x in range(120,144):
                for y in range(120,144): tiles[x,y,1]=[ROOF]
        buildings.append(ix)
        for x,idx in ((130,0),(129,1),(128,2)):
            put(tiles,x,128,-1,'fixtures_stairs_01_'+str(idx)); tiles.pop((x,128,0),None)
        entrances.append(dict(x=cx*256+127,y=cy*256+128,z=0,
            bottom=[cx*256+131,cy*256+128,-1],rect=[cx*256+120,cy*256+120,24,24]))
    buildings.append(indices)
    return dict(entrances=entrances,caches=caches,area=total_area,
                levels=[-2,-1],stairs=2 if shaft else 1,
                tunnelAxes=dict(x=[126,131],y=[126,131]))
