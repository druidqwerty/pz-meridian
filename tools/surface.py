"""Sparse authored corridor with wooded verges and fully natural B42 hinterland."""
from random import Random
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import box
from atlas import pieces

MATERIALS={'water':1,'verge':2,'town':3,'road':4}
SPRITES=['blends_natural_01_16','blends_natural_02_0','blends_natural_01_32',
         'blends_natural_01_16','blends_street_01_86']


def raster(cx,cy,features):
    image=Image.new('L',(256,256),0)
    active=Image.new('1',(256,256),0)
    clip=box(cx*256,cy*256,(cx+1)*256,(cy+1)*256)
    priority={'water':0,'town':1,'verge':2,'road':3}
    for geom,material,_ in sorted(features,key=lambda r:priority[r[1]]):
        for p in pieces(geom.intersection(clip)):
            coords=[(round(x-cx*256),round(y-cy*256)) for x,y in p.exterior.coords]
            ImageDraw.Draw(image).polygon(coords,fill=MATERIALS[material])
            ImageDraw.Draw(active).polygon(coords,fill=1)
    ground=np.array(image)
    chunks=np.asarray(active).reshape(32,8,32,8).any(axis=(1,3))
    # A small complete-chunk shoulder prevents wilderness trees on the asphalt.
    mask=np.repeat(np.repeat(chunks,8,axis=0),8,axis=1)
    tiles={(int(x),int(y),0):[SPRITES[int(ground[y,x])]] for y,x in zip(*np.nonzero(mask))}
    return ground,tiles


def dress(cx,cy,ground,tiles,town=False):
    rng=Random(cx*7919+cy*104729)
    # Hand-authored trees use verified vanilla tree sheet, not custom artwork.
    for (x,y,z),names in list(tiles.items()):
        if z or ground[y,x] not in (0,2):continue
        near=ground[max(0,y-3):min(256,y+4),max(0,x-3):min(256,x+4)]
        if 4 in near:continue
        if rng.random()<(.008 if town else .035):
            names.append('vegetation_trees_01_'+str(rng.choice([8,9,10,11,13,14,15])))
    # Edge paint leaves the actual lane centre clear; no collision props.
    road=ground==4
    for y,x in zip(*np.nonzero(road)):
        if x and not road[y,x-1] and y%5<3:
            tiles[int(x),int(y),0].append('street_trafficlines_01_0')


def city_wall(cx,cy,tiles,rooms=None,buildings=None):
    from fortification import build_wall
    return build_wall(cx,cy,tiles,rooms,buildings)
