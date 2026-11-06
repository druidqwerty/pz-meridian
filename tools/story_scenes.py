"""Physical archive desks and convoy traces, not a new quest/event system."""
from furnishing import EXTRAS

# Existing thirteen readable archives remain the only interaction. The caravan
# props are native furniture: they neither spawn vehicles nor award progression.
CONVOY = {0:'assembly',1:'overnight',3:'water-diversion',5:'repair',
          8:'forest-camp',10:'screening',12:'arrival'}


def archive_desk(tiles,x,y,w,h,kind):
    if kind not in ('civic','lab','cottage','archive','museum','postoffice'):
        return None
    xx,yy=x+w//2+3,y+h-2
    tiles.setdefault((xx,yy,0),[]).append('location_business_office_generic_01_16')
    return [xx,yy,0]


def convoy_trace(tiles,ground,cx,cy,records,site):
    if not site or site['id'] not in CONVOY or not records:return None
    # Keep the main road, shaft reserve, actual rooms and all entrance aprons.
    props=[]
    def free(x,y):
        if not(8<=x<248 and 8<=y<248):return False
        if ground[y,x] in (1,4):return False
        if 116<=x<=148 and 116<=y<=148:return False
        for rec in records:
            a,b,w,h=rec['rect'];a-=cx*256;b-=cy*256
            if a-3<=x<=a+w+3 and b-3<=y<=b+h+5:return False
        names=tiles.get((x,y,0),[])
        return len(names)==1 and names[0].startswith(('blends_','floors_exterior_'))
    # Paired abandoned belongings/fieldtables carry a visual motif along route.
    for x,y in ((52,60),(56,60),(60,60),(52,64),(60,64),(56,68)):
        if not free(x,y):continue
        key=('chest','crate','side','chair','basket','metal')[len(props)%6]
        sprite=EXTRAS.get(key,'appliances_laundry_01_24')
        tiles[x,y,0].append(sprite)
        if key=='side':tiles[x,y,0].append(EXTRAS['radio'])
        props.append(dict(x=cx*256+x,y=cy*256+y,z=0,sprite=sprite))
    return dict(stage=CONVOY[site['id']],objects=props)
