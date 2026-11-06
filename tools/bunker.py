"""Original two-level continuity habitat, linked across native-cell boundaries.

Six-wide axial galleries join all cells. Residential, medical, military and
laboratory wings have real rooms, vanilla furniture and physical doors/stairs.
"""
from architecture import put,wall as _wall,room_furniture,TILE,ROOF,PAVING,TILES
from obstacles import tunnel_obstacles
from habitat import wing_for,role_for,room_name,wing_summary
from room_lighting import place_room_lighting


def wall(tiles,x,y,z,direction,kind='solid',palette=16):
    """Vanilla steel doors, with the correct N/W closed/open sprite family."""
    _wall(tiles,x,y,z,direction,kind,palette)
    if kind == 'door':
        tiles[x,y,z][-1] = 'fixtures_doors_01_'+str(69 if direction == 'N' else 68)


def cover_bunker(tiles,coverage,shaft):
    """Flat roof underlays retain existing surface art and all stair apertures.

    Viewpoint 0.1.6.1 RoofLevels.flatRoof tests sprite names through its bundled
    roof-pieces.txt (roofs_01_22 = flat), not an invented tile flag. Placing the
    marker before the existing floor preserves terrain and every surface object.
    """
    count = 0
    for z, points in coverage.items():
        for x,y in points:
            if (z == -2 and y == 136 and 128 <= x <= 130) or (
                    shaft and z == -1 and y == 128 and 128 <= x <= 130):
                continue
            names = tiles.setdefault((x,y,z+1),[])
            if ROOF not in names:
                names.insert(0,ROOF); count += 1
    return count

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
    room_start=len(rooms)
    loX,hiX,loY,hiY=[config[k] for k in ('minCX','maxCX','minCY','maxCY')]
    if not(loX<=cx<=hiX and loY<=cy<=hiY): return dict(entrances=[],caches=[])
    shaft=(cx in (loX,hiX) or cy in (loY,hiY))
    entrances=[]; caches=[]; indices=[]; total_area=0; coverage={}; obstacles=[]
    wing=wing_for(cx,cy,config)
    room_roles=[]
    for z in (-2,-1):
        owner={}; specs=[dict(name='hall',role='hall')]; doors=set()
        def fill(x,y,w,h,i=0):
            for xx in range(x,x+w):
                for yy in range(y,y+h): owner[xx,yy]=i
        fill(0,126,256,6); fill(126,0,6,256); fill(120,120,24,24)
        # Four-wide service ring makes four independent loops around the wings.
        # It joins both original axes; no cell-seam or stair location is moved.
        fill(12,12,232,4); fill(12,240,232,4)
        fill(12,16,4,224); fill(240,16,4,224)
        for q,(qx,qy) in enumerate(((16,16),(144,16),(16,144),(144,144))):
            fill(16 if qx==16 else 132,qy+40,116 if qx==16 else 108,16)
            for col in range(3):fill(qx+col*32-4,qy,4,96)
            big=(cx+cy+q+z)%5==0
            if big:
                i=len(specs); role=role_for(wing,q,0,0,z)
                specs.append(dict(name=room_name(role),role=role,rect=(qx,qy,96,96)))
                fill(qx,qy,96,96,i)
                doors.add((qx+96 if qx==16 else qx,qy+48,'W'))
                doors.update((qx,qy+dy,'W') for dy in (24,72))
            else:
                for row in range(2):
                    for col in range(3):
                        rx,ry=qx+col*32,qy+row*56
                        role=role_for(wing,q,row,col,z)
                        i=len(specs); specs.append(dict(name=room_name(role),role=role,rect=(rx,ry,28,40)))
                        fill(rx,ry,28,40,i)
                        doors.add((rx+14,ry+40 if row==0 else ry,'N'))
                        doors.add((rx,ry+20,'W'))
        total_area+=len(owner); coverage[z]=set(owner)
        for i,spec in enumerate(specs):
            points={p for p,n in owner.items() if n==i}
            if not points: continue
            indices.append(len(rooms)); rooms.append(dict(name=spec['name'],level=z,
                rects=rects_for(points),objects=[]))
            floor=wing['floor'] if spec['role'] in ('hall','assembly','livingroom','bedroom') else TILE
            for xx,yy in points: tiles[xx,yy,z]=[floor]
            if 'rect' not in spec: continue
            x,y,w,h=spec['rect']
            room_roles.append(dict(role=spec['role'],name=spec['name'],z=z,
                                   rect=[cx*256+x,cy*256+y,w,h]))
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
        # Fire compartments across both axial galleries: real openable steel
        # door pairs, never force-locked props or a teleport bypass.
        for along in (48,208):
            for across in range(126,132):
                kind='door' if across in (128,129) else 'solid'
                wall(tiles,along,across,z,'W',kind,0)
                wall(tiles,across,along,z,'N',kind,0)
        obstacles.extend(tunnel_obstacles(tiles,cx,cy,z))
    # Stairs -2 -> -1. Landing is west of the top, bottom approach east.
    for x,idx in ((130,0),(129,1),(128,2)):
        put(tiles,x,136,-2,'fixtures_stairs_01_'+str(idx)); tiles.pop((x,136,-1),None)
    if shaft:
        # Architectural entrance is a guarded masonry pavilion, not a teleport.
        ix=[]
        for z in (0,):
            ix.append(len(rooms)); rooms.append(dict(name='hall',level=z,rects=[(120,120,24,24)],objects=[]))
            for x in range(120,144):
                for y in range(120,144): tiles[x,y,z]=[wing['floor']]
            for x in range(120,144):
                wall(tiles,x,120,z,'N','window' if x%6==2 else 'solid',0)
                wall(tiles,x,144,z,'N','door' if x in (131,132) else 'solid',0)
            for y in range(120,144):
                for x in (120,144): wall(tiles,x,y,z,'W','window' if y%6==2 else 'solid',0)
            for x in range(120,144):
                for y in range(120,144): tiles[x,y,1]=[ROOF]
            # Actual receiving/use scene distinguishes surface access pavilions.
            # The broad centre, paired south doors and both stair approaches stay empty.
            entry_role=wing['entrance'][0]
            if entry_role in ('medical','staff','isolation'):
                props=((122,122,'cart'),(123,122,'medicine'),(141,122,'metal'))
            elif entry_role in ('cargo','maintenance','water','power'):
                props=((122,122,'crate'),(123,122,'crate'),(141,122,'metal'))
            elif entry_role in ('research','records','command'):
                props=((122,122,'files'),(123,122,'desk'),(141,122,'shelves'))
            else:
                props=((122,122,'chair'),(123,122,'chair'),(141,122,'shelves'))
            for x,y,key in props:put(tiles,x,y,0,TILES[key])
        buildings.append(ix)
        for x,idx in ((130,0),(129,1),(128,2)):
            put(tiles,x,128,-1,'fixtures_stairs_01_'+str(idx)); tiles.pop((x,128,0),None)
        erole,en,ru=wing['entrance']
        entrances.append(dict(x=cx*256+127,y=cy*256+128,z=0,
            bottom=[cx*256+131,cy*256+128,-1],rect=[cx*256+120,cy*256+120,24,24],
            role=erole,name=en,nameRU=ru,wing=wing['id']))
    buildings.append(indices)
    ceiling_tiles=cover_bunker(tiles,coverage,shaft)
    lighting=[]
    for rr in rooms[room_start:]:
        lighting.extend(place_room_lighting(tiles,rr))
    return dict(entrances=entrances,caches=caches,area=total_area,
                levels=[-2,-1],stairs=2 if shaft else 1,
                wing=wing_summary(wing),roomRoles=room_roles,
                serviceRing=dict(rect=[12,12,232,232],width=4),
                obstacles=obstacles,ceilingTiles=ceiling_tiles,lighting=lighting,
                metalDoorSprites=['fixtures_doors_01_68','fixtures_doors_01_69'],
                bulkheads=[dict(x=cx*256+48,y=cy*256+128,z=z,direction='W',
                    sprite='fixtures_doors_01_68') for z in (-2,-1)],
                tunnelAxes=dict(x=[126,131],y=[126,131]))
