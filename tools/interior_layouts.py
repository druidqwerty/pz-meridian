"""Furniture clusters, complete grid objects and explicit walking clearances."""
from furniture_orientation import facing, BED_GROUPS, SOFA_GROUPS, MEDICAL_GROUP


class Interior:
    def __init__(self, x, y, w, h, names, blocked):
        self.x, self.y, self.w, self.h, self.names = x, y, w, h, names
        self.out = {}
        self.blocked = {(p[0]-x, p[1]-y) for p in blocked}

    def free(self, dx, dy):
        # The central E-W crossing connects side-door approaches; outer rim
        # keeps N/S doors reachable. Explicit geometry paths are reserved too.
        return (1 <= dx < self.w-1 and 0 <= dy < self.h-1 and
                (dx, dy) not in self.blocked and
                (dx, dy) not in self.out and
                not (self.h >= 6 and dy == self.h//2))

    def group(self, dx, dy, group):
        if not all(self.free(dx+a, dy+b) for a, b, _ in group):
            return False
        for a, b, sprite in group:
            self.out[dx+a, dy+b] = [sprite]
        return True

    def add(self, dx, dy, key, direction='S', top=None):
        if not self.group(dx, dy, ((0, 0, facing(key, direction, self.names)),)):
            return False
        if top:
            self.top(dx, dy, top)
        return True

    def top(self, dx, dy, key):
        if (dx, dy) in self.out:
            self.out[dx, dy].append(self.names[key])

    def dining(self, dx, dy):
        # Matching seats look toward, not away from, their table.
        return self.group(dx, dy, ((0, 0, self.names['table']),
            (0, 1, facing('chair', 'N')), (1, 0, facing('chair', 'W'))))

    def dump(self):
        for (dx, dy), sprites in self.out.items():
            for sprite in sprites:
                yield self.x+dx, self.y+dy, sprite


def furnish_room(role, x, y, w, h, seed, base, blocked=()):
    f = Interior(x, y, w, h, base, blocked)
    if w < 3 or h < 3:
        return
    if role == 'gunstorestorage':
        role = 'armystorage'
    if role == 'departmentstore':
        role = 'grocery'
    if role in ('kitchen', 'restaurantkitchen'):
        for dx, key in ((1, 'fridge'), (2, 'oven'), (3, 'counter')):
            f.add(dx, 0, key, 'S')
        f.top(3, 0, 'sink_south')
        for dx in range(4, w-1):
            f.add(dx, 0, 'counter', 'S', 'microwave' if dx == 4 else
                  'coffee' if dx == 5 else None)
        if w >= 7 and h >= 6:
            f.dining(2, h-3)
        f.add(w-2, h-2, 'bin')
    elif role in ('bedroom', 'hospitalroom', 'medical'):
        medical = role != 'bedroom'
        for dx in range(1, w-2, 4 if medical else 5):
            # Alternate whole oriented objects, never independent bed parts.
            direction = 'E' if seed % 2 and not medical else 'S'
            f.group(dx, 0, MEDICAL_GROUP if medical else BED_GROUPS[direction])
            side_x = dx+2 if direction == 'E' else dx+1
            f.add(side_x, 0, 'side', top='lamp')
        f.add(w-2, h-2, 'metal' if medical else 'dresser', 'N')
        if w >= 7:
            f.add(1, h-2, 'shelves', 'N')
            f.add(w-3, h-2, 'desk', 'N', 'radio')
            f.add(w-3, h-3, 'chair', 'S')
        if w >= 10 and h >= 8:
            f.add(3, h-2, 'dresser', 'N')
            f.add(4, h-2, 'side', top='flowers')
        if medical:
            f.add(w-2, 0, 'counter', 'S', 'sink_south')
            f.add(1, h-2, 'cart')
    elif role in ('bathroom', 'shower'):
        f.add(1, 0, 'toilet', 'S')
        f.add(w-2, 0, 'counter', 'S', 'sink_south')
        f.top(w-2, 0, 'medicine')
        if w >= 6:
            f.add(3, 0, 'shower')
        f.add(1, h-2, 'bin')
        if role == 'shower':
            for dx in range(3, w-2, 2):
                f.add(dx, 0, 'shower'); f.add(dx, h-2, 'metal', 'N')
    elif role in ('livingroom', 'hall', 'waitingroom'):
        f.group(1, 0, SOFA_GROUPS['S'])
        f.add(3, 0, 'side', top='lamp')
        f.add(w-2, 0, 'plant')
        if h >= 5:
            f.add(1, 2, 'lowtable')
            f.add(1, h-2, 'side', top='tv')
            f.add(w-2, h-2, 'shelves', 'N')
        if w >= 8 and h >= 7:
            f.add(w-3, 1, 'armchair', 'W')
            f.add(w-3, h-2, 'desk', 'N', 'phone')
            f.add(w-3, h-3, 'chair', 'S')
            f.add(3, h-2, 'side', top='radio')
        if w >= 11 and h >= 8:
            f.dining(w-5, h-4)
    elif role in ('laboratory', 'office', 'classroom', 'communications'):
        for dx in range(1, w-2, 3):
            f.add(dx, 0, 'counter' if role == 'laboratory' else 'desk', 'S',
                  'microscope' if role == 'laboratory' else
                  'radio' if role == 'communications' else 'computer' if role == 'office' else None)
            f.add(dx, 1, 'chair', 'N')
            if h >= 9:
                f.add(dx, h-3, 'desk', 'N')
                f.add(dx, h-4, 'chair', 'S')
        if role == 'classroom' and h >= 12:
            for dx in range(1, w-2, 3):
                for dy in range(3, h-4, 3):
                    f.group(dx, dy, ((0, 0, facing('desk', 'S')),
                                     (0, 1, facing('chair', 'N'))))
        f.add(w-2, h-2, 'shelves', 'N')
        f.add(1, h-2, 'bin')
    elif role in ('storage', 'armystorage', 'medicalstorage', 'policestorage',
                  'grocery', 'gasstore', 'library', 'archive'):
        storage = role.endswith('storage') or role == 'storage'
        key = 'metal' if storage else 'files' if role == 'archive' else 'shelves'
        for dx in range(1, w-1, 2 if storage else 3):
            f.add(dx, 0, key, 'S'); f.add(dx, h-2, key, 'N')
            if h >= 10:
                for dy in range(3, h-3, 4):
                    f.add(dx, dy, 'crate' if storage else 'shelves', 'S')
        if role in ('grocery', 'gasstore'):
            f.add(w-2, 1, 'fridge', 'W')
        f.add(w-3, h-3, 'desk', 'N', 'phone')
    else:
        from interior_scenes import furnish_scene
        furnish_scene(f, role, seed)
    # Repeatable lived-in variation is independent from safe furniture facing.
    # Only low supported props vary, never appliances or half of a grid object.
    supports = [(dx, dy) for (dx, dy), names in f.out.items()
                if len(names) == 1 and names[0] in
                {base.get('side'), facing('dresser', 'S'), facing('desk', 'S'),
                 facing('desk', 'N'), facing('counter', 'S')}]
    if supports:
        dx, dy = supports[seed % len(supports)]
        f.top(dx, dy, 'radio' if seed % 2 else 'flowers')
    yield from f.dump()
