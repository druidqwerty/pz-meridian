"""Native, thirteen-tile-deep eight-storey Meridian enceinte, not a flat fence."""

FLOOR = 'floors_exterior_tilesandstone_01_0'
WALL_W = 'walls_exterior_house_02_16'
WALL_N = 'walls_exterior_house_02_17'
HEIGHT, OUTER, INNER = 8, 2, 15
GATE_Y, GATE_HALF = 1536, 10


def build_wall(cx, cy, tiles, rooms=None, buildings=None):
    if not (188 <= cx <= 191 and 4 <= cy <= 7):
        return None
    rooms = [] if rooms is None else rooms
    buildings = [] if buildings is None else buildings
    x0, y0 = cx*256, cy*256
    strips = []
    if cy == 4: strips.append((0, OUTER, 256, INNER-OUTER, 'north'))
    if cy == 7: strips.append((0, 256-INNER, 256, INNER-OUTER, 'south'))
    if cx == 188: strips.append((OUTER, 0, INNER-OUTER, 256, 'west'))
    if cx == 191: strips.append((256-INNER, 0, INNER-OUTER, 256, 'east'))
    if not strips:
        return None
    indices, points = [], set()
    for x,y,w,h,_ in strips:
        points.update((xx,yy) for xx in range(x,x+w) for yy in range(y,y+h))
    # Bastion at the gate's north shoulder; stays clear of the nearest city plot.
    stair = cx == 188 and cy == 5
    if stair:
        points.update((x,y) for x in range(OUTER,19) for y in range(216,245))
    for z in range(HEIGHT+1):
        active = {p for p in points if not (cx == 188 and
            abs(y0+p[1]-GATE_Y) <= GATE_HALF and z < 4)}
        for x,y in active:
            tiles[x,y,z] = [FLOOR]
        # Exact disjoint rectangles, including corners and open gate, for native
        # indoor roomlight support. No overlapping RoomDefs at a corner joint.
        from bunker import rects_for
        rects = rects_for(active)
        if rects:
            indices.append(len(rooms))
            rooms.append(dict(name='hall',level=z,rects=rects,objects=[]))
        for x,y in active:
            # Outer shell, inner shell and gate jambs. Cell seams remain open
            # when they meet the next same-height rampart cell.
            for dx,dy,sprite in ((-1,0,WALL_W),(0,-1,WALL_N)):
                neighbor=x+dx,y+dy
                if neighbor in active: continue
                if x+dx < 0 and cx > 188: continue
                if y+dy < 0 and cy > 4: continue
                # Public ground-level entry into bastion staircase.
                if stair and z == 0 and x == 18 and 230 <= y <= 232: continue
                tiles[x,y,z].append(sprite)
            for dx,dy,sprite in ((1,0,WALL_W),(0,1,WALL_N)):
                neighbor=x+dx,y+dy
                if neighbor in active: continue
                nx,ny=neighbor
                if nx >= 256 or ny >= 256: continue
                if stair and z == 0 and nx == 19 and 230 <= y <= 232: continue
                tiles.setdefault((nx,ny,z),[]).append(sprite)
        if stair and z > 0:
            for x in (4,5,6): tiles.pop((x,232,z),None)
        if stair and z < HEIGHT:
            for x,i in ((6,0),(5,1),(4,2)):
                tiles.setdefault((x,232,z),[]).append('fixtures_stairs_01_'+str(i))
    # A paved twelve-tile entry approach makes the staircase reachable from the
    # city side; wall shell is open only here, never across the perimeter face.
    if stair:
        for x in range(18,24):
            for y in range(230,233): tiles[x,y,0]=[FLOOR]
    buildings.append(indices)
    from room_lighting import place_room_lighting
    for index in indices:
        # Open-air crown is not an electrically enclosed room.
        if rooms[index]['level'] < HEIGHT:
            place_room_lighting(tiles,rooms[index])
    return dict(height=HEIGHT,depth=INNER-OUTER,walkwayZ=HEIGHT,
        rects=[list(r[:4]) for r in strips],
        gateClearWidth=GATE_HALF*2+1,gateClearHeight=4,
        stairs=dict(bottom=[x0+7,y0+232,0],top=[x0+3,y0+232,HEIGHT]) if stair else None)
