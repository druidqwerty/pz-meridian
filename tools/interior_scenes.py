"""Functional activity clusters for schools, services and technical buildings."""
from furniture_orientation import facing


def furnish_scene(f, role, seed):
    w, h = f.w, f.h
    if role == 'gunstore':
        for dx in range(1, w-1, 2):
            f.add(dx, 0, 'gunrack')
            f.add(dx, h-2, 'counter', 'N')
        f.add(1, h-3, 'metal', 'E')
        f.add(w-2, h-3, 'desk', 'W', 'phone')
    elif role == 'laundry':
        for i, dx in enumerate(range(1, w-1, 2)):
            f.add(dx, 0, 'washer' if i % 2 == 0 else 'dryer')
            f.add(dx, h-2, 'basket')
        f.add(w-2, h-3, 'counter', 'W')
        f.add(1, h-3, 'table')
    elif role in ('workshop', 'pump', 'electrical', 'garage'):
        for dx in range(1, w-1, 3):
            f.add(dx, 0, 'tools' if role in ('workshop', 'garage') else 'metal')
            f.add(dx, h-2, 'counter', 'N', 'radio' if role == 'electrical' else None)
            if role in ('workshop', 'garage'):
                f.add(dx, 1, 'grinder')
            if role == 'pump':
                f.add(dx+1, 0, 'counter', 'S', 'sink_south')
        f.add(1, h-3, 'crate'); f.add(w-2, h-3, 'bin')
        if h >= 10:
            for dx in range(2, w-2, 4):
                f.add(dx, h-4, 'metalcrate')
    elif role == 'nursery':
        for dx in range(1, w-2, 3):
            f.add(dx, 0, 'lowtable', top='flowers')
            f.add(dx, 1, 'chair', 'N'); f.add(dx, h-2, 'shelves', 'N')
        if w >= 8 and h >= 8:
            f.dining(w-4, h-4)
        f.add(w-2, 0, 'chest'); f.add(w-2, h-2, 'plant')
    elif role == 'gym':
        for dx in range(1, w-1, 2):
            f.add(dx, 0, 'metal'); f.add(dx, h-2, 'chair', 'N')
        f.add(1, h-3, 'chest'); f.add(w-2, h-3, 'chest')
    elif role == 'assembly':
        # Rows turn toward a real front table; breaks between banks keep aisles.
        for dx in range(1, w-2, 2):
            for dy in range(2, h-2, 2):
                if dx not in (w//2-1, w//2):
                    f.add(dx, dy, 'chair', 'N')
        f.add(1, 0, 'desk', 'S', 'radio')
        f.add(w-2, 0, 'plant')
    else:
        # Storage is a sensible native fallback, never an empty undefined room.
        for dx in range(1, w-1, 3):
            f.add(dx, 0, 'metal', 'S')
        f.add(1, h-2, 'desk', 'N')
