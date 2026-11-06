"""Write native IGMB paper map from original clipped geometry."""
from xml.etree.ElementTree import Element, SubElement, ElementTree
from shapely.geometry import box
from worldmap_binary import write_binary


def pieces(g):
    if g.geom_type=='Polygon':
        yield g
    elif hasattr(g,'geoms'):
        for child in g.geoms:
            yield from pieces(child)


def write_atlas(folder,by_cell,records):
    root=Element('world',version='1.0',cellSize='256')
    for (cx,cy),features in sorted(by_cell.items()):
        cell=SubElement(root,'cell',x=str(cx),y=str(cy))
        clip=box(cx*256,cy*256,(cx+1)*256,(cy+1)*256)
        shapes=[(g,p) for g,m,p in features if p]
        shapes += [(box(*[r['rect'][0],r['rect'][1],r['rect'][0]+r['rect'][2],r['rect'][1]+r['rect'][3]]),
                    ('building','Residential' if r['kind']=='house' else 'CommunityServices'))
                   for r in records if r['rect'][0]//256==cx and r['rect'][1]//256==cy]
        for shape,prop in shapes:
            for poly in pieces(shape.intersection(clip)):
                points=[]
                for x,y in list(poly.exterior.coords)[:-1]:
                    p=(max(0,min(256,round(x-cx*256))),max(0,min(256,round(y-cy*256))))
                    if not points or p!=points[-1]:points.append(p)
                if len(set(points))<3:continue
                f=SubElement(cell,'feature')
                g=SubElement(f,'geometry',type='Polygon')
                coords=SubElement(g,'coordinates')
                for x,y in points:SubElement(coords,'point',x=str(x),y=str(y))
                props=SubElement(f,'properties')
                SubElement(props,'property',name=prop[0],value=prop[1])
    xml=folder/'worldmap.xml'
    ElementTree(root).write(xml,encoding='utf-8',xml_declaration=True)
    return write_binary(xml)
