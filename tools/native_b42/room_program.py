"""Purpose-led furnishing policy. Targets apply to non-circulation floor area."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Programme:
    clusters: tuple[str, ...]
    density: tuple[float, float] = (.18, .38)
    empty_side: int = 5
    open_activity: bool = False
    service: str | None = None


PROGRAMMES = {
    'kitchen': Programme(('dining', 'prep', 'dining', 'pantry'), service='kitchen'),
    'restaurantkitchen': Programme(('prep', 'pantry', 'prep'), service='kitchen'),
    'dining': Programme(('dining', 'dining', 'coffee'), service='refreshments'),
    'office': Programme(('workstations', 'files', 'workstations', 'meeting')),
    'communications': Programme(('communications', 'files', 'meeting')),
    'classroom': Programme(('students', 'students', 'books'), service='teacher'),
    'laboratory': Programme(('lab', 'medicalstorage', 'lab')),
    'medical': Programme(('ward', 'medicalstorage', 'ward')),
    'hospitalroom': Programme(('ward', 'ward', 'medicalstorage')),
    'dormitory': Programme(('bunks', 'lockers', 'bunks')),
    # Oversized private bedrooms are suites, never unrequested barracks.
    'bedroom': Programme(('lounge', 'study', 'wardrobe'), (.15, .36),
                         service='bedroom'),
    'livingroom': Programme(('lounge', 'books', 'study'), (.15, .36)),
    'waitingroom': Programme(('lounge', 'lounge', 'reception'), (.15, .36)),
    'library': Programme(('books', 'study', 'books')),
    'archive': Programme(('files', 'files', 'study'), (.22, .42)),
    'storage': Programme(('racks', 'racks', 'packing'), (.26, .48)),
    'armystorage': Programme(('lockers', 'racks', 'packing'), (.26, .48)),
    'policestorage': Programme(('lockers', 'racks', 'packing'), (.26, .48)),
    'medicalstorage': Programme(('medicalstorage', 'racks'), (.26, .48)),
    'grocery': Programme(('shop', 'shop', 'packing'), (.24, .46)),
    'gasstore': Programme(('shop', 'shop', 'coffee')),
    'gunstore': Programme(('weapons', 'lockers', 'reception')),
    'laundry': Programme(('laundry', 'folding', 'laundry')),
    'workshop': Programme(('workbench', 'tools', 'packing')),
    'electrical': Programme(('electrical', 'lockers', 'workbench')),
    'pump': Programme(('utility', 'lockers')),
    'nursery': Programme(('play', 'books', 'play'), (.15, .35)),
    'assembly': Programme(('seats', 'seats', 'seats'), service='teacher'),
    'hall': Programme(('lounge', 'reception'), (.05, .20), 10, True),
    'gym': Programme(('lockers', 'rest'), (.05, .20), 16, True),
    'garage': Programme(('tools', 'workbench'), (.05, .20), 16, True),
    'bathroom': Programme(('washroom',), (.18, .40)),
    'shower': Programme(('showers', 'lockers'), (.18, .40)),
}
ALIASES = {'departmentstore': 'grocery', 'gunstorestorage': 'armystorage',
           'canteen': 'dining', 'cafeteria': 'dining', 'restaurant': 'dining',
           'warehouse': 'storage', 'ward': 'medical', 'lounge': 'livingroom'}


def programme(role):
    role = ALIASES.get(role, role)
    if role not in PROGRAMMES:
        raise ValueError(f'No furnishing programme for {role!r}; supply its purpose')
    return role, PROGRAMMES[role]


def activity_order(role, policy, x, y, w, h, seed):
    """Legible functional districts, not arbitrary checkerboards of appliances."""
    if role == 'kitchen':
        return ('dining',) if y >= h//2 else (('pantry',) if x >= w*2//3 else ('prep',))
    if role == 'restaurantkitchen':
        return ('pantry',) if x >= w*2//3 else ('prep',)
    if role in ('office', 'communications', 'classroom'):
        main = {'office': 'workstations', 'communications': 'communications',
                'classroom': 'students'}[role]
        if x >= w*3//4:
            return ('books',) if role == 'classroom' else ('files',)
        if role == 'office' and y >= h*3//4:
            return ('meeting',)
        return (main,)
    if role in ('bedroom', 'livingroom', 'waitingroom'):
        if x >= w*2//3:
            return ('wardrobe',) if role == 'bedroom' else ('books',)
        return ('study',) if y < h//3 else ('lounge',)
    offset = (x//4+y//4+seed) % len(policy.clusters)
    return policy.clusters[offset:]+policy.clusters[:offset]
