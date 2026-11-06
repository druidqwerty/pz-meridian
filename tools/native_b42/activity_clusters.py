"""Atomic activity groups: footprint plus supported, purpose-specific decoration."""
from dataclasses import dataclass
from .furniture_orientation import facing, BED_GROUPS, SOFA_GROUPS, MEDICAL_GROUP

# B42.21 local tiles metadata verified; extend new recipes without altering
# the original hash-bound imported tables. Gun racks have no N/W variant.
EXTRA_FACING = {
    'files': {'S': 'location_business_office_generic_01_16',
              'E': 'location_business_office_generic_01_17',
              'N': 'location_business_office_generic_01_24',
              'W': 'location_business_office_generic_01_25'},
    'tools': {'S': 'location_business_machinery_01_32',
              'E': 'location_business_machinery_01_33',
              'N': 'location_business_machinery_01_34',
              'W': 'location_business_machinery_01_35'},
}


@dataclass(frozen=True)
class Cluster:
    name: str
    parts: tuple  # (dx, dy, sprite layers); first layer is the floor footprint

    @property
    def size(self):
        return (max(x for x, _, _ in self.parts)+1,
                max(y for _, y, _ in self.parts)+1)


def cluster(name, base):
    def p(x, y, key, direction='S', top=None):
        sprite = (EXTRA_FACING[key][direction] if key in EXTRA_FACING else
                  facing(key, direction, base))
        layers = (sprite,)
        if top:
            layers += (base[top],)
        return x, y, layers

    def grid(group):
        return [(x, y, (sprite,)) for x, y, sprite in group]

    if name == 'kitchen_compact':
        parts = [p(0, 0, 'fridge', 'N'), p(1, 0, 'oven', 'N'),
                 p(2, 0, 'counter', 'N', 'sink'),
                 p(0, 1, 'counter', top='microwave'),
                 p(1, 1, 'counter', top='coffee'), p(2, 1, 'counter')]
    elif name == 'kitchen':
        parts = [p(0, 0, 'fridge'), p(1, 0, 'oven'),
                 p(2, 0, 'counter', top='sink_south'), p(3, 0, 'counter'),
                 p(4, 0, 'counter', top='microwave'),
                 p(5, 0, 'counter', top='coffee')]
    elif name == 'refreshments':
        parts = [p(0, 0, 'counter', top='coffee'), p(1, 0, 'counter'),
                 p(2, 0, 'bin')]
    elif name == 'bedroom':
        parts = grid(BED_GROUPS['S'])+[p(1, 0, 'side', top='lamp'),
                                     p(2, 0, 'dresser')]
    elif name == 'teacher':
        parts = [p(0, 0, 'desk'), p(1, 0, 'desk'), p(0, 1, 'chair', 'N')]
    elif name == 'dining':
        parts = [p(1, 1, 'table'), p(0, 1, 'chair', 'E'),
                 p(2, 1, 'chair', 'W'), p(1, 0, 'chair', 'S'),
                 p(1, 2, 'chair', 'N')]
    elif name in ('prep', 'folding', 'packing', 'coffee'):
        top = 'coffee' if name == 'coffee' else None
        parts = [p(x, y, 'counter' if name == 'prep' else 'table',
                   'N' if y == 0 else 'S', top if (x, y) == (0, 1) else None)
                 for x in range(2) for y in range(2)]
    elif name in ('workstations', 'communications', 'students', 'lab'):
        key = 'counter' if name == 'lab' else 'desk'
        top = {'workstations': 'computer', 'communications': 'radio',
               'students': None, 'lab': 'microscope'}[name]
        parts = [p(x, 0, key, top=top) for x in range(2)]
        parts += [p(x, 1, 'chair', 'N') for x in range(2)]
    elif name in ('study', 'reception', 'meeting'):
        parts = [p(0, 0, 'desk', top='phone' if name == 'reception' else None),
                 p(1, 0, 'desk'), p(0, 1, 'chair', 'N'),
                 p(1, 1, 'chair', 'N')]
    elif name in ('ward', 'bunks'):
        parts = grid(MEDICAL_GROUP if name == 'ward' else BED_GROUPS['S'])
        parts += [p(1, 0, 'metal' if name == 'ward' else 'side'),
                  p(2, 0, 'cart' if name == 'ward' else 'dresser')]
    elif name == 'lounge':
        parts = grid(SOFA_GROUPS['S'])+[p(0, 2, 'lowtable'),
                 p(2, 0, 'side', top='lamp'), p(2, 2, 'armchair', 'W')]
    elif name in ('racks', 'lockers', 'pantry', 'files', 'books', 'shop',
                  'medicalstorage', 'wardrobe', 'weapons', 'tools'):
        key = {'racks': 'metal', 'lockers': 'metal', 'pantry': 'shelves',
               'files': 'files', 'books': 'shelves', 'shop': 'shelves',
               'medicalstorage': 'metal', 'wardrobe': 'dresser',
               'weapons': 'gunrack', 'tools': 'tools'}[name]
        # Back-to-back shelving; BOTH fronts open to protected local aisles.
        parts = [p(x, y, key, 'N' if y == 0 and name != 'weapons' else 'S')
                 for x in range(3) for y in range(1 if name == 'weapons' else 2)]
    elif name in ('workbench', 'electrical', 'utility'):
        parts = [p(0, 0, 'counter', top='radio' if name == 'electrical' else None),
                 p(1, 0, 'counter', top='sink_south' if name == 'utility' else None),
                 p(2, 0, 'metal'), p(3, 0, 'crate')]
    elif name == 'laundry':
        parts = [p(0, 0, 'washer'), p(1, 0, 'dryer'), p(2, 0, 'basket'),
                 p(2, 1, 'table')]
    elif name == 'play':
        parts = [p(0, 0, 'lowtable'), p(1, 0, 'lowtable'),
                 p(0, 1, 'chair', 'N'), p(1, 1, 'chair', 'N')]
    elif name == 'seats':
        # Never put a second chair row directly behind the first: every row
        # needs its own reachable approach, not merely a group bounding apron.
        parts = [p(x, 0, 'chair', 'N') for x in range(3)]
    elif name == 'rest':
        parts = [p(0, 0, 'chair'), p(1, 0, 'chair'), p(2, 0, 'bin')]
    elif name == 'washroom':
        parts = [p(0, 0, 'toilet'), p(2, 0, 'counter', top='sink_south')]
    elif name == 'showers':
        parts = [p(0, 0, 'shower'), p(2, 0, 'shower')]
    else:
        raise ValueError(f'Unknown activity cluster: {name}')
    return Cluster(name, tuple(parts))
