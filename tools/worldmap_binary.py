"""Original B42 IGMB v2 writer, verified against installed WorldMapBinary.

B42.21's XML reader confuses short-coordinate count with point count. Ship
the binary beside XML: the game's normal asset loader prefers the binary.
The input XML here is already 256-tile cells (do not rescale it from 300).
"""
from pathlib import Path
import struct
from xml.etree import ElementTree
from shapely import make_valid, set_precision
from shapely.geometry import Polygon


def _polygons(value):
    if value.is_empty:
        return
    if value.geom_type == 'Polygon':
        yield value
    elif hasattr(value,'geoms'):
        for child in value.geoms:
            yield from _polygons(child)


def write_binary(xml_path):
    xml_path = Path(xml_path)
    root = ElementTree.parse(xml_path).getroot()
    if root.get('cellSize') != '256':
        raise ValueError('This writer requires 256-tile source cells')
    cells, strings = {}, {'Polygon', 'LineString'}
    repaired = 0
    for cell in root.findall('cell'):
        key = int(cell.get('x')),int(cell.get('y'))
        if min(key)<0:
            raise ValueError('Binary map writer requires nonnegative cells')
        features = []
        for feature in cell.findall('feature'):
            geometry = feature.find('geometry')
            kind = geometry.get('type')
            if kind not in ('Polygon', 'LineString'):
                raise ValueError('Unsupported map geometry')
            rings = [[(int(p.get('x')),int(p.get('y'))) for p in r.findall('point')]
                     for r in geometry.findall('coordinates')]
            props = [(p.get('name'),p.get('value','')) for p in feature.findall('properties/property')]
            strings.update(item for pair in props for item in pair)
            if kind == 'LineString':
                if len(rings) != 1 or not 2 <= len(rings[0]) <= 32767 or len(set(rings[0])) < 2:
                    raise ValueError('Map line needs one path with at least two distinct points')
                features.append((kind,rings,props))
                continue
            shape = Polygon(rings[0],rings[1:])
            repaired += not shape.is_valid
            shape = set_precision(make_valid(shape),1.0,mode='valid_output')
            for polygon in _polygons(shape):
                if polygon.area<1:
                    continue
                outlines = [[(int(x),int(y)) for x,y in list(r.coords)[:-1]]
                            for r in [polygon.exterior,*polygon.interiors]]
                if not polygon.is_valid or len(outlines)>255 or any(len(r)>32767 for r in outlines):
                    raise ValueError('Map polygon exceeds native geometry constraints')
                features.append((kind,outlines,props))
        if sum(len(r) for _,rings,_ in features for r in rings)*2 > 32767:
            raise ValueError(f'Cell {key} exceeds signed-short coordinate-buffer budget')
        if features:
            cells[key] = features
    if not cells:
        raise ValueError('No world-map features')
    names = sorted(strings)
    if len(names)>32767:
        raise ValueError('World-map string table too large')
    index = {name:i for i,name in enumerate(names)}
    width,height = max(x for x,y in cells)+1,max(y for x,y in cells)+1
    data = bytearray(b'IGMB'+struct.pack('<5i',2,256,width,height,len(names)))
    for name in names:
        raw = name.encode('utf-8')
        if len(raw)>1022:
            raise ValueError('World-map string exceeds engine read buffer')
        data.extend(struct.pack('<h',len(raw))+raw)
    count = 0
    for y in range(height):
        for x in range(width):
            features = cells.get((x,y))
            if not features:
                data.extend(struct.pack('<i',-1))
                continue
            data.extend(struct.pack('<3i',x,y,len(features)))
            for kind,rings,props in features:
                data.extend(struct.pack('<hB',index[kind],len(rings)))
                for ring in rings:
                    data.extend(struct.pack('<h',len(ring)))
                    for px,py in ring:
                        if not 0<=px<=256 or not 0<=py<=256:
                            raise ValueError('Map geometry coordinate outside its cell')
                        data.extend(struct.pack('<hh',px,py))
                if len(props)>255:
                    raise ValueError('Too many feature properties')
                data.extend(struct.pack('<B',len(props)))
                for key,value in props:
                    data.extend(struct.pack('<hh',index[key],index[value]))
                count += 1
    destination = xml_path.with_name(xml_path.name+'.bin')
    destination.write_bytes(data)
    return dict(path=str(destination),cells=len(cells),features=count,
                repaired_geometries=repaired,bytes=len(data))


if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xml',type=Path)
    args=parser.parse_args()
    print(json.dumps(write_binary(args.xml),indent=2))
