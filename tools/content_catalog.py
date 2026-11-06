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
    """Four identifiable districts, not the same eight buildings in every cell.

    Plots stay inside the existing64tile grid and out of the shaft reservation.
    The northwest medical site used by previous live QA is retained.
    """
    if cx < 190 and cy < 6:
        zone = 'civic'; kinds = ['apartment','house','shop','civic','hospital',
            'archive','school','police','library','kindergarten','museum','gym',
            'clinic','laundry','house','shop']
    elif cx >= 190 and cy < 6:
        zone = 'residential'; kinds = ['house','apartment','house','kindergarten',
            'shop','laundry','house','clinic','house','apartment','school','house',
            'library','gym','house','shop']
    elif cx < 190:
        zone = 'utilities'; kinds = ['depot','workshop','warehouse','waterworks',
            'laundry','warehouse','house','gatehouse','workshop','relay','warehouse',
            'fuel','house','clinic','warehouse','diner']
    else:
        zone = 'council'; kinds = ['house','house','civic','library','house','house',
            'museum','archive','house','clinic','civic','house','gym','house',
            'shop','house']
    return zone, [dict(x=x,y=y,kind=kinds[i]) for i,(x,y) in enumerate(
        ( (x,y) for x in (24,88,152,216) for y in (24,88,152,216) ))]
