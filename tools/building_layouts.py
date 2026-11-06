"""Original, function-specific floor plans; all rectangles are native RoomDefs.

The circulation room is always first. Its southern landing preserves the native
three-tile westward stair flight. Other rooms carry a separate furnishing theme.
No exterior picture or third-party floor plan is imported into the product.
"""

DOMESTIC = {'house','cottage','ranch','duplex','rowhouse','farm','camp'}
TOWERS = {'midrise','officeblock','residentialtower','officetower','apartment'}
SERVICE = {'garage','workshop','depot','warehouse','scrapyard','waterworks',
           'firestation','terminal','gym','chapel'}


def segments(length, weights):
    """Integer contiguous bands, with no zero-width or uncovered seam."""
    cuts=[0]
    total=sum(weights)
    for i in range(1,len(weights)):
        cuts.append(round(length*sum(weights[:i])/total))
    cuts.append(length)
    return list(zip(cuts[:-1],cuts[1:]))


def layout(w,h,roles,kind,seed=0,z=0,levels=1):
    landing=4 if levels>1 else 2
    top=h-landing
    hallw=3 if levels>1 or w>=24 else 2
    mid=(w-hallw)//2
    hall=[(mid,0,hallw,top),(0,top,w,landing)]
    rooms=[dict(name='hall',rects=hall,theme='hall')]

    def add(name,rect,theme=None):
        a,b,c,d=rect
        if c<3 or d<3:raise ValueError((kind,'Room too narrow',rect))
        rooms.append(dict(name=name,rects=[rect],theme=theme or name))

    def bands(x,width,names,start=0,end=None,themes=None,weights=None):
        end=top if end is None else end
        for i,(a,b) in enumerate(segments(end-start,weights or [1]*len(names))):
            add(names[i],(x,start+a,width,b-a),themes[i] if themes else None)

    if kind=='bigboxmall':
        from mall_layout import mall_rooms
        rooms=mall_rooms(w,h,landing)
    elif kind=='gunshop':
        add('gunstore',(0,0,mid,top),'gunstore')
        bands(mid+hallw,w-mid-hallw,['gunstorestorage','office','bathroom'],
              weights=[6,5,5],themes=['storage','office','bathroom'])
    elif kind=='guardhut':
        # A real tiny sentry shelter, not a scaled-down four-room house.
        rooms[0]['rects']=[(0,top,w,landing)]
        add('office',(0,0,w,top),'communications')
    elif kind in SERVICE:
        # Deep service bay and smaller side offices, rather than quadrants.
        spine=max(8,w-11); hall[0]=(spine,0,3,top)
        add('hall' if kind in ('gym','chapel','terminal') else 'storage',
            (0,0,spine,top),
            'gym' if kind=='gym' else 'assembly' if kind in ('chapel','terminal') else
            'pump' if kind=='waterworks' else 'workshop' if kind!='warehouse' else 'storage')
        if top>=12:
            bands(spine+3,w-spine-3,['office','storage','bathroom'],weights=[4,4,3])
        else:
            bands(spine+3,w-spine-3,['office','bathroom'])
    elif kind=='ranch':
        # L-shaped rear court: the unowned northeast corner stays outdoors.
        mid=10;hall[0]=(mid,0,2,top)
        bands(0,mid,['kitchen','livingroom'],weights=[5,7])
        bands(mid+2,w-mid-2,['bedroom','bathroom'],start=6,weights=[6,4])
    elif kind in DOMESTIC:
        if kind=='duplex':
            for a,width in ((0,mid),(mid+hallw,w-mid-hallw)):
                bands(a,width,['kitchen','bedroom','livingroom','bathroom'],
                      weights=[5,6,6,3])
        elif kind=='rowhouse':
            bands(0,mid,['kitchen','livingroom'] if z==0 else ['bedroom','bedroom'])
            bands(mid+hallw,w-mid-hallw,['livingroom','bathroom'] if z==0 else
                  ['bedroom','bathroom'],weights=[7,4])
        else:
            # Asymmetric domestic rooms and a compact two-tile entry hall.
            bands(0,mid,['kitchen','livingroom'],weights=[5,6])
            bands(mid+hallw,w-mid-hallw,['bedroom','bathroom'],weights=[7,4])
    elif kind in TOWERS:
        office=kind in ('officeblock','officetower')
        if z==0:
            bands(0,mid,['office','grocery','storage'],weights=[5,7,4])
            bands(mid+hallw,w-mid-hallw,['office','hall','bathroom'],
                  weights=[5,7,4],themes=['office','assembly','bathroom'])
        elif office:
            bands(0,mid,['office','office','office','office'])
            bands(mid+hallw,w-mid-hallw,['office','office','storage','bathroom'])
        else:
            # Two complete domestic suites per storey, not giant dormitories.
            for a,width in ((0,mid),(mid+hallw,w-mid-hallw)):
                bands(a,width,['kitchen','bedroom','livingroom','bathroom'],
                      weights=[5,7,7,3])
    elif kind in ('school','kindergarten'):
        bands(0,mid,['classroom']*3 if kind=='school' else ['classroom','livingroom'],
              themes=['classroom']*3 if kind=='school' else ['nursery','livingroom'])
        bands(mid+hallw,w-mid-hallw,['library','office','bathroom'],weights=[5,5,3])
    elif kind in ('police','checkpoint','gatehouse','military','barracks'):
        bands(0,mid,['policestorage' if kind=='police' else 'armystorage','office'])
        bands(mid+hallw,w-mid-hallw,['office','bedroom','bathroom'],weights=[4,5,3],
              themes=['communications','bedroom','bathroom'])
    elif kind in ('shop','generalstore','stripmall','fuel','gas','diner','motel'):
        if kind=='stripmall':
            bands(0,mid,['grocery','grocery','grocery'])
            bands(mid+hallw,w-mid-hallw,['storage','office','bathroom'])
        elif kind=='motel':
            bands(0,mid,['bedroom','bedroom','bedroom'])
            bands(mid+hallw,w-mid-hallw,['bedroom','bedroom','bathroom'])
        else:
            add('kitchen' if kind=='diner' else 'gasstore' if kind in ('fuel','gas') else 'grocery',
                (0,0,mid,top))
            bands(mid+hallw,w-mid-hallw,
                  ['livingroom','bathroom'] if kind=='diner' else ['storage','bathroom'],
                  themes=['assembly','bathroom'] if kind=='diner' else None,weights=[7,3])
    elif kind in ('hospital','clinic','sanatorium','vet','lab'):
        bands(0,mid,['laboratory','laboratory','medicalstorage'] if kind=='lab' else
              ['hospitalroom','medical','medicalstorage'],weights=[5,5,4])
        bands(mid+hallw,w-mid-hallw,['office','medical','bathroom'],weights=[5,5,4])
    else:
        # Public programmes vary the number and proportions of their rooms.
        names=list(roles)
        bands(0,mid,names[:2],weights=[6,5])
        bands(mid+hallw,w-mid-hallw,names[2:],weights=[7,4])

    owners={}
    for i,room in enumerate(rooms):
        for a,b,c,d in room['rects']:
            for xx in range(a,a+c):
                for yy in range(b,b+d):
                    if (xx,yy) in owners:raise ValueError((kind,'overlapping rooms',xx,yy))
                    owners[xx,yy]=i
    doors=set()
    for i in range(1,len(rooms)):
        candidates=[]
        for (xx,yy),owner in owners.items():
            if owner!=i:continue
            for dx,dy,direction in ((-1,0,'W'),(1,0,'W'),(0,-1,'N'),(0,1,'N')):
                if owners.get((xx+dx,yy+dy))==0:
                    candidates.append((max(xx,xx+dx),max(yy,yy+dy),direction))
        if not candidates:raise ValueError((kind,'room does not reach circulation',i))
        doors.add(candidates[len(candidates)//2])
    return rooms,doors,owners
