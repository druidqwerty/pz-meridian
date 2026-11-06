"""An original two-storey shopping centre; no imported floor-plan assets."""


def mall_rooms(w,h,landing):
    middle=(w-4)//2
    cross=30
    top=h-landing
    hall=[(middle,0,4,top),(0,cross,middle,6),
          (middle+4,cross,w-middle-4,6),(0,top,w,landing)]
    result=[dict(name='hall',theme='hall',rects=hall)]
    def room(name,rect,theme=None):
        result.append(dict(name=name,rects=[rect],theme=theme or name))
    left=middle//2
    room('departmentstore',(0,0,left,cross),'grocery')
    room('sportstore',(left,0,middle-left,cross),'grocery')
    room('departmentstore',(middle+4,0,w-middle-4,cross),'grocery')
    height=top-cross-6
    room('hall',(0,cross+6,left,height),'assembly')
    room('kitchen',(left,cross+6,middle-left,height))
    right=(w-middle-4)//2
    hall.append((middle+4+right-3,cross+6,3,height))
    room('departmentstore',(middle+4,cross+6,right-3,height),'grocery')
    xx=middle+4+right
    room('storage',(xx,cross+6,w-xx,height//2))
    room('office',(xx,cross+6+height//2,w-xx,height//4))
    room('bathroom',(xx,cross+6+height*3//4,w-xx,height-height*3//4))
    return result
