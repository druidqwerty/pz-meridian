"""Native compound building programmes; no runtime rules or new item systems."""

# Native room names retain the shipped game's loot distributions. Display/theme
# roles below only change furniture: a workshop still uses native storage loot.
KINDS = {
 'motel': (30,26,2,('bedroom','bedroom','livingroom','bathroom')),
 'diner': (30,22,1,('kitchen','livingroom','storage','bathroom')),
 'depot': (32,28,1,('storage','storage','office','bathroom')),
 'visitor': (28,24,1,('library','office','livingroom','bathroom')),
 'weighstation': (24,20,1,('office','storage','office','bathroom')),
 'terminal': (32,28,2,('hall','office','storage','bathroom')),
 'camp': (24,22,1,('kitchen','bedroom','livingroom','bathroom')),
 'chapel': (30,26,1,('hall','library','office','bathroom')),
 'scrapyard': (30,24,1,('storage','storage','office','bathroom')),
 'vet': (28,24,1,('medical','medicalstorage','office','bathroom')),
 'farm': (28,24,2,('kitchen','bedroom','livingroom','bathroom')),
 'waterworks': (32,28,1,('storage','storage','office','bathroom')),
 'relay': (30,26,2,('office','storage','office','bathroom')),
 'archive': (32,28,2,('library','office','library','bathroom')),
 'museum': (32,28,2,('hall','library','office','bathroom')),
 'sanatorium': (32,28,2,('hospitalroom','medical','bedroom','bathroom')),
 'workshop': (30,24,1,('storage','storage','office','bathroom')),
 'postoffice': (32,28,2,('storage','office','storage','bathroom')),
 'gatehouse': (24,22,1,('office','armystorage','livingroom','bathroom')),
 'library': (32,28,2,('library','library','office','bathroom')),
 'laundry': (30,24,1,('laundry','laundry','office','bathroom')),
 'gym': (32,28,1,('gym','gym','storage','bathroom')),
 'kindergarten': (30,26,1,('classroom','livingroom','kitchen','bathroom')),
 'ranch': (28,20,1,('kitchen','bedroom','livingroom','bathroom')),
 'duplex': (30,26,2,('kitchen','bedroom','livingroom','bathroom')),
 'rowhouse': (20,28,3,('kitchen','bedroom','livingroom','bathroom')),
 'garage': (20,16,1,('storage','office','storage','bathroom')),
 'guardhut': (10,10,1,('office','office','office','office')),
 'generalstore': (20,20,1,('grocery','storage','office','bathroom')),
 'stripmall': (34,30,1,('grocery','grocery','office','bathroom')),
 'firestation': (32,28,2,('storage','bedroom','office','bathroom')),
 'checkpoint': (18,18,1,('armystorage','office','office','bathroom')),
 'midrise': (28,30,5,('kitchen','bedroom','livingroom','bathroom')),
 'officeblock': (30,30,6,('office','office','storage','bathroom')),
 'residentialtower': (32,32,10,('kitchen','bedroom','livingroom','bathroom')),
 'officetower': (34,32,12,('office','office','storage','bathroom')),
 'gunshop': (24,20,1,('gunstore','gunstorestorage','office','bathroom')),
 'bigboxmall': (96,72,2,('departmentstore','grocery','kitchen','bathroom')),
}

THEMES = {
 'motel': ('bedroom','bedroom','livingroom','bathroom'),
 'diner': ('kitchen','assembly','storage','bathroom'),
 'depot': ('workshop','storage','office','bathroom'),
 'weighstation': ('communications','workshop','office','bathroom'),
 'terminal': ('assembly','communications','storage','bathroom'),
 'chapel': ('assembly','library','office','bathroom'),
 'scrapyard': ('workshop','workshop','office','bathroom'),
 'waterworks': ('pump','electrical','office','bathroom'),
 'relay': ('communications','electrical','office','bathroom'),
 'archive': ('archive','office','archive','bathroom'),
 'museum': ('assembly','archive','office','bathroom'),
 'workshop': ('workshop','workshop','office','bathroom'),
 'postoffice': ('archive','office','storage','bathroom'),
 'laundry': ('laundry','laundry','office','shower'),
 'gym': ('gym','gym','storage','shower'),
 'kindergarten': ('nursery','livingroom','kitchen','bathroom'),
}


def city_program(cx, cy):
    """Dense metropolitan skyline over four different working districts.

    Every lot fits the street grid; shafts remain in the reserved centre strips.
    Over half the city stock has six or more occupied storeys. Homes and service
    buildings remain between towers, instead of replacing the city with offices.
    """
    sub = (cx % 2) * 2 + (cy % 2)
    if cx < 190 and cy < 6:
        zone = 'civic'
        base = [
            ['officetower','residentialtower','officetower','civic',
             'hospital','residentialtower','school','police','officeblock','officetower',
             'residentialtower','officetower','clinic','officeblock','house','residentialtower'],
            ['officetower','civic','residentialtower','police',
             'officeblock','officetower','library','firestation','residentialtower','officetower',
             'archive','residentialtower','postoffice','officeblock','gunshop','officetower'],
            ['residentialtower','officetower','museum','officeblock',
             'officetower','hospital','residentialtower','civic','officetower','police',
             'school','officetower','diner','residentialtower','shop','officeblock'],
            ['officeblock','officetower','residentialtower','chapel',
             'officetower','clinic','officeblock','firestation','residentialtower','officetower',
             'gym','residentialtower','stripmall','officetower','house','officeblock'],
        ][sub]
    elif cx >= 190 and cy < 6:
        zone = 'residential'
        base = [
            ['residentialtower','house','residentialtower','kindergarten',
             'stripmall','residentialtower','house','clinic','residentialtower','officeblock',
             'school','residentialtower','duplex','residentialtower','house','residentialtower'],
            ['residentialtower','apartment','residentialtower','cottage',
             'generalstore','residentialtower','rowhouse','diner','residentialtower','midrise',
             'gym','residentialtower','ranch','residentialtower','house','officeblock'],
            ['residentialtower','duplex','residentialtower','school',
             'shop','residentialtower','apartment','laundry','residentialtower','midrise',
             'chapel','residentialtower','house','residentialtower','cottage','officetower'],
            ['residentialtower','rowhouse','residentialtower','kindergarten',
             'diner','residentialtower','house','clinic','residentialtower','apartment',
             'library','residentialtower','duplex','residentialtower','gunshop','officeblock'],
        ][sub]
    elif cx < 190:
        zone = 'utilities'
        base = [
            ['depot','workshop','officeblock','waterworks',
             'laundry','residentialtower','house','gatehouse','firestation','relay',
             'officeblock','fuel','residentialtower','clinic','warehouse','diner'],
            ['warehouse','firestation','officeblock','depot',
             'gunshop','residentialtower','garage','police','workshop','officetower',
             'officeblock','fuel','residentialtower','scrapyard','terminal','motel'],
            ['depot','garage','officetower','warehouse',
             'workshop','residentialtower','firestation','checkpoint','officeblock','relay',
             'military','fuel','residentialtower','weighstation','laundry','diner'],
            ['warehouse','workshop','officeblock','terminal',
             'depot','residentialtower','gunshop','police','firestation','officetower',
             'officeblock','gas','residentialtower','garage','barracks','shop'],
        ][sub]
    else:
        zone = 'council'
        base = [
            ['officetower','residentialtower','officetower','officeblock',
             'residentialtower','officetower','museum','residentialtower','officetower',
             'residentialtower','officeblock','officetower','residentialtower','officetower',
             'library','residentialtower'],
            ['officetower','officeblock','residentialtower','officetower',
             'residentialtower','officetower','archive','residentialtower','officetower',
             'officeblock','residentialtower','officetower','civic','officetower',
             'police','residentialtower'],
            ['residentialtower','officetower','officeblock','officetower',
             'officetower','residentialtower','sanatorium','officetower','residentialtower',
             'officetower','officeblock','residentialtower','postoffice','officetower',
             'gunshop','residentialtower'],
            ['officetower','residentialtower','officetower','officeblock',
             'residentialtower','officetower','hospital','residentialtower','officetower',
             'residentialtower','officeblock','officetower','firestation','officetower',
             'diner','residentialtower'],
        ][sub]
    coords = [(x, y) for x in (24, 88, 152, 216) for y in (24, 88, 152, 216)]
    return zone, [
        dict(x=x, y=y, kind=base[i], variant=((cx - 188) * 23 + (cy - 4) * 7 + i * 3) % 100)
        for i, (x, y) in enumerate(coords)
    ]
