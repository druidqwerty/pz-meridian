"""Standalone original route-plan figure, not a game screenshot or asset export."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from world import make_plan,ROUTE,SIZE,SAFE
from expedition_sites import CHAPTERS

ROOT=Path(__file__).resolve().parents[1]
COLORS=('#d97e52','#9b9a45','#8d83a6','#4f94ad','#4c977b','#c46867','#d9b46a')


def font(size,bold=False):
    name='arialbd.ttf' if bold else 'arial.ttf'
    path=Path('C:/Windows/Fonts')/name
    return ImageFont.truetype(str(path),size)


def polygons(geometry):
    if geometry.geom_type=='Polygon':yield geometry
    elif hasattr(geometry,'geoms'):
        for child in geometry.geoms:yield from polygons(child)


def main():
    features,_,sites=make_plan()
    image=Image.new('RGB',(1780,1240),'#101d24');draw=ImageDraw.Draw(image)
    origin=(60,110);scale=1040/SIZE
    def point(x,y):return (origin[0]+x*scale,origin[1]+y*scale)
    draw.text((60,30),'MERIDIAN — THE LONG WAY HOME',font=font(34,True),fill='#edf0e9')
    draw.text((60,76),'128.256 km principal road · original fictional region · B42.21',font=font(18),fill='#afc4c7')
    draw.rectangle((*origin,origin[0]+1040,origin[1]+1040),fill='#263d38',outline='#58746f',width=2)
    for geometry,material,prop in features:
        color={'water':'#365e75','town':'#48604f'}.get(material)
        if color:
            for poly in polygons(geometry):draw.polygon([point(x,y) for x,y in poly.exterior.coords],fill=color)
        if material=='road' and prop and prop[1] in ('secondary','service'):
            for poly in polygons(geometry):
                draw.line([point(x,y) for x,y in poly.exterior.coords],fill='#8ca9a1',width=1)
    for index,chapter in enumerate(CHAPTERS):
        a,b=chapter[3],min(chapter[4],1)
        positions=[ROUTE.interpolate(a+(b-a)*step/100,normalized=True) for step in range(101)]
        draw.line([point(p.x,p.y) for p in positions],fill=COLORS[index],width=5)
        p=ROUTE.interpolate((a+b)/2,normalized=True);x,y=point(p.x,p.y)
        draw.ellipse((x-11,y-11,x+11,y+11),fill=COLORS[index],outline='#edf0e9',width=2)
        draw.text((x-5,y-8),chr(65+index),font=font(13,True),fill='#111f25')
    for site in sites:
        if site.get('kind')=='expedition':
            x,y=point(site['x'],site['y'])
            if site['category']!='landmark':
                r=3 if site['category']=='stop' else 5
                draw.rectangle((x-r,y-r,x+r,y+r),fill='#d8e0cc')
    landmarks=[s for s in sites if s.get('category')=='landmark']
    for number,site in enumerate(landmarks,1):
        x,y=point(site['x'],site['y'])
        draw.ellipse((x-12,y-12,x+12,y+12),fill='#e8e7d5',outline='#15262c',width=2)
        label=str(number);draw.text((x-(8 if number==10 else 4),y-8),label,font=font(13,True),fill='#15262c')
    for label,coord,offset in [('LAST LIGHT',(512,48640),(14,-27)),('MERIDIAN',(48640,1536),(-137,20))]:
        x,y=point(*coord)
        draw.ellipse((x-7,y-7,x+7,y+7),fill='#f5d37b',outline='#11202a',width=2)
        draw.text((x+offset[0],y+offset[1]),label,font=font(16,True),fill='#f5d37b',stroke_width=2,stroke_fill='#15262c')
    lx=1150
    draw.text((lx,110),'SEVEN ROAD CHAPTERS',font=font(23,True),fill='#edf0e9')
    for i,chapter in enumerate(CHAPTERS):
        y=154+i*37
        draw.rounded_rectangle((lx,y,lx+28,y+26),radius=5,fill=COLORS[i])
        draw.text((lx+8,y+3),chr(65+i),font=font(17,True),fill='#15262c')
        draw.text((lx+43,y+2),chapter[1],font=font(19),fill='#d3e1dd')
    draw.text((lx,445),'TEN LANDMARK COMPOUNDS',font=font(23,True),fill='#edf0e9')
    for i,site in enumerate(landmarks,1):
        y=493+(i-1)*45
        draw.text((lx,y),f'{i:02}  {site["name"]}',font=font(17,True),fill='#e7e7d7')
        draw.text((lx+35,y+21),f'{site["x"]}, {site["y"]}',font=font(13),fill='#8ca8a6')
    draw.text((lx,975),'12 roadside stops · 7 possible bases',font=font(19,True),fill='#d3e1dd')
    draw.text((lx,1005),'6 regional detours · local service loops',font=font(18),fill='#a8c3bb')
    draw.text((lx,1055),'N ↑       Native tile scale: 1 tile ≈ 1 metre',font=font(17),fill='#afc4c7')
    draw.line((lx,1110,lx+10000*scale,1110),fill='#edf0e9',width=4)
    draw.text((lx,1123),'0                         10 km',font=font(14),fill='#afc4c7')
    draw.text((60,1180),'Planning schematic — not gameplay rendering. Service buildings and loops are enlarged for legibility.',font=font(17),fill='#afc4c7')
    draw.text((60,1208),'Original geometry © 2026 druidqwerty · MIT · No game artwork or textures used in this figure.',font=font(15),fill='#708b8b')
    target=ROOT/'docs/route-map.png';image.save(target,optimize=True)
    print(f'{target.name}: {image.width}x{image.height}; {len(landmarks)} landmarks; {len(CHAPTERS)} chapters')


if __name__=='__main__':main()
