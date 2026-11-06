"""Original B42.21 native map codec; no game assets are embedded.

Format references: installed IsoLot, LotHeader and IsoMetaGrid bytecode;
KnoxMap MIT format documentation (rust/knoxlots/src/{header,pack,cell}.rs).
Cells are 256 tiles; chunks are 8 tiles. All numeric fields are little endian.
Missing squares are RLE skips, allowing vanilla wilderness generation.
"""
from pathlib import Path
import struct

CELL, CHUNK, COUNT = 256, 8, 1024
NONE = 0xFFFFFFFF


def _numbers(*values):
    return struct.pack('<' + 'I' * len(values), *(v & NONE for v in values))


def _line(value):
    if not value or '\n' in value or '\r' in value or '\x00' in value:
        raise ValueError(f'Invalid native map name: {value!r}')
    return value.encode('ascii') + b'\n'


def _room_index(rooms):
    index = {}
    for number, room in enumerate(rooms):
        level = room.get('level', room.get('z', 0))
        if not -32 <= level <= 31 or not room['rects']:
            raise ValueError('Room requires a valid level and nonempty rectangles')
        for x, y, w, h in room['rects']:
            if min(x, y) < 0 or min(w, h) <= 0 or x+w > CELL or y+h > CELL:
                raise ValueError(f'Room rectangle outside cell: {(x,y,w,h)}')
            for xx in range(x, x+w):
                for yy in range(y, y+h):
                    key = xx, yy, level
                    if key in index and index[key] != number:
                        raise ValueError(f'Overlapping rooms at {key}')
                    index[key] = number
    return index


def _check_buildings(rooms, buildings):
    linked = []
    for building in buildings:
        if not building:
            raise ValueError('Empty building')
        for room in building:
            if not 0 <= room < len(rooms):
                raise ValueError(f'Unknown building room {room}')
            linked.append(room)
    if sorted(linked) != list(range(len(rooms))):
        raise ValueError('Every room must belong to exactly one building')


def write_cell(path, cx, cy, tiles, rooms=None, buildings=None, zombie_density=0):
    """Write a native pair; return paths/counts. Tiles are local (x,y,z)->[sprite].

    Rooms: {name, level, rects:[(x,y,w,h)], objects:[(kind,x,y)]}; buildings
    list room-index lists. A room omitted from buildings is rejected. Density
    is a byte, a 1024-byte x-major sequence, or fn(local_chunk_x,local_chunk_y).
    B42 MetaGridLoaderThread reads file[x*32+y], then stores the *internal*
    LotHeader array[y*32+x]. Do not transpose the on-disk grid to match that API.
    No offset may point at zero: every empty chunk has an actual RLE record.
    """
    rooms = rooms or []
    buildings = buildings or []
    _check_buildings(rooms, buildings)
    room_at = _room_index(rooms)
    levels = [0] + [r.get('level', r.get('z', 0)) for r in rooms]
    for (x, y, z), sprites in tiles.items():
        if not 0 <= x < CELL or not 0 <= y < CELL or not -32 <= z <= 31:
            raise ValueError(f'Tile outside cell or levels: {(x,y,z)}')
        if not sprites:
            raise ValueError(f'Use an absent key, not an empty tile record: {(x,y,z)}')
        levels.append(z)
    low, high = min(levels), max(levels)
    names = sorted({name for sprites in tiles.values() for name in sprites})
    number = {name: i for i, name in enumerate(names)}
    header = bytearray(b'LOTH' + _numbers(1, len(names)))
    for name in names:
        header.extend(_line(name))
    header.extend(_numbers(8, 8, low, high, len(rooms)))
    for room in rooms:
        header.extend(_line(room['name']))
        header.extend(_numbers(room.get('level', room.get('z', 0)), len(room['rects'])))
        for rect in room['rects']:
            header.extend(_numbers(*rect))
        objects = room.get('objects', [])
        header.extend(_numbers(len(objects)))
        for obj in objects:
            if len(obj) != 3:
                raise ValueError('Metaobject is (kind,x,y)')
            header.extend(_numbers(*obj))
    header.extend(_numbers(len(buildings)))
    for building in buildings:
        header.extend(_numbers(len(building), *building))
    if isinstance(zombie_density, int) and not 0 <= zombie_density <= 255:
        raise ValueError('Zombie density must be an unsigned byte (0..255)')
    if callable(zombie_density):
        density = bytes(zombie_density(x, y) for x in range(32) for y in range(32))
    elif isinstance(zombie_density, int):
        density = bytes([zombie_density]) * COUNT
    else:
        density = bytes(zombie_density)
    if len(density) != COUNT:
        raise ValueError('Zombie density must contain 1024 bytes')
    header.extend(density)
    # Sorted names make builds deterministic. RLE can cross level boundaries.
    chunks, offsets = [], []
    current = 12 + COUNT * 8
    for chunk_x in range(32):
        for chunk_y in range(32):
            body, run = bytearray(), 0
            for z in range(low, high+1):
                for x in range(chunk_x*8, chunk_x*8+8):
                    for y in range(chunk_y*8, chunk_y*8+8):
                        sprites = tiles.get((x,y,z))
                        if sprites is None:
                            run += 1
                            continue
                        if run:
                            body.extend(_numbers(NONE, run))
                            run = 0
                        body.extend(_numbers(len(sprites)+1, room_at.get((x,y,z), NONE)))
                        body.extend(_numbers(*(number[name] for name in sprites)))
            if run:
                body.extend(_numbers(NONE, run))
            offsets.append(current)
            chunks.append(body)
            current += len(body)
    pack = bytearray(b'LOTP' + _numbers(1, COUNT))
    pack.extend(struct.pack('<1024Q', *offsets))
    for chunk in chunks:
        pack.extend(chunk)
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    hpath, ppath = target / f'{cx}_{cy}.lotheader', target / f'world_{cx}_{cy}.lotpack'
    hpath.write_bytes(header)
    ppath.write_bytes(pack)
    return dict(header=str(hpath), pack=str(ppath), squares=len(tiles),
                rooms=len(rooms), buildings=len(buildings), bytes=len(header)+len(pack))


class _Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, size):
        end = self.pos + size
        if size < 0 or end > len(self.data):
            raise ValueError('Truncated native map record')
        value = self.data[self.pos:end]
        self.pos = end
        return value

    def uint(self):
        return struct.unpack('<I', self.take(4))[0]

    def sint(self):
        return struct.unpack('<i', self.take(4))[0]

    def line(self):
        end = self.data.find(b'\n', self.pos)
        if end < 0 or end-self.pos > 4096:
            raise ValueError('Missing or oversized map string')
        return self.take(end-self.pos+1)[:-1].decode('ascii')

    def count(self):
        value = self.uint()
        if value > 1_000_000:
            raise ValueError('Implausible native map record count')
        return value


def read_cell(path, cx, cy):
    """Decode and structurally validate v1 native files without game dependencies."""
    target = Path(path)
    h = _Reader((target / f'{cx}_{cy}.lotheader').read_bytes())
    if h.take(4) != b'LOTH' or h.uint() != 1:
        raise ValueError('Expected B42 LOTH version 1')
    names = [h.line() for _ in range(h.count())]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate tile name')
    if (h.uint(), h.uint()) != (8,8):
        raise ValueError('B42 chunks must be 8x8')
    low, high = h.sint(), h.sint()
    if not -32 <= low <= high <= 31:
        raise ValueError('Invalid native height range')
    rooms = []
    for _ in range(h.count()):
        room = dict(name=h.line(), level=h.sint())
        room['rects'] = [tuple(h.uint() for _ in range(4)) for _ in range(h.count())]
        room['objects'] = [tuple(h.uint() for _ in range(3)) for _ in range(h.count())]
        rooms.append(room)
    buildings = [[h.uint() for _ in range(h.count())] for _ in range(h.count())]
    _check_buildings(rooms, buildings)
    density = h.take(COUNT)
    if h.pos != len(h.data):
        raise ValueError('Trailing native header bytes')
    p = _Reader((target / f'world_{cx}_{cy}.lotpack').read_bytes())
    if p.take(4) != b'LOTP' or p.uint() != 1 or p.uint() != COUNT:
        raise ValueError('Expected B42 LOTP version 1, 1024 chunks')
    offsets = list(struct.unpack('<1024Q', p.take(COUNT*8))) + [len(p.data)]
    if offsets[0] != p.pos or any(a >= b for a,b in zip(offsets,offsets[1:])):
        raise ValueError('Invalid native chunk offsets')
    tiles, room_ids = {}, {}
    expected = (high-low+1)*64
    for chunk, (start, end) in enumerate(zip(offsets, offsets[1:])):
        if end > len(p.data):
            raise ValueError('Chunk extends past file')
        r, square = _Reader(p.data[start:end]), 0
        while square < expected:
            count = r.uint()
            if count == NONE:
                skip = r.uint()
                if not 1 <= skip <= expected-square:
                    raise ValueError(f'Invalid RLE run in chunk {chunk}')
                square += skip
                continue
            if not 2 <= count <= 4096:
                raise ValueError('Tile record must have room and one or more sprites')
            room_id = r.uint()
            if room_id != NONE and room_id >= len(rooms):
                raise ValueError('Tile points to an unknown room')
            sprites = []
            for _ in range(count-1):
                number = r.uint()
                if number >= len(names):
                    raise ValueError('Tile index outside native string table')
                sprites.append(names[number])
            key = (chunk//32*8 + square%64//8,
                   chunk%32*8 + square%8, low+square//64)
            tiles[key], room_ids[key] = sprites, room_id
            square += 1
        if r.pos != len(r.data):
            raise ValueError(f'Extra records in chunk {chunk}')
    return dict(tiles=tiles, rooms=rooms, buildings=buildings, zombie_density=density,
                min_level=low, max_level=high, room_ids=room_ids, names=names)


def audit_cell(path, cx, cy, expected_tiles=None):
    """Validate a built cell, spatial room assignment, and optional exact tile oracle."""
    value = read_cell(path, cx, cy)
    room_at = _room_index(value['rooms'])
    for key, number in value['room_ids'].items():
        if number != room_at.get(key, NONE):
            raise ValueError(f'Tile room disagrees with room rectangles at {key}')
    if expected_tiles is not None and value['tiles'] != expected_tiles:
        raise ValueError('Native round trip changed tile positions or sprite order')
    return dict(cell=[cx,cy], squares=len(value['tiles']), rooms=len(value['rooms']),
                buildings=len(value['buildings']), tilesets=len(value['names']),
                levels=[value['min_level'],value['max_level']])


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Audit one B42 native map cell')
    parser.add_argument('path')
    parser.add_argument('cx', type=int)
    parser.add_argument('cy', type=int)
    args = parser.parse_args()
    print(json.dumps(audit_cell(args.path, args.cx, args.cy), indent=2))
