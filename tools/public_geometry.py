"""Reusable tile-mask geometry, independent of Meridian or sprite names."""
from collections import deque
import numpy as np


def dilate(mask, radius=1):
    """Square grid dilation; edge extrapolation keeps through-roads seam-safe."""
    height, width = mask.shape
    padded = np.pad(mask, radius, mode='edge')
    result = np.zeros_like(mask, dtype=bool)
    for dy in range(2*radius+1):
        for dx in range(2*radius+1):
            result |= padded[dy:dy+height, dx:dx+width]
    return result


def exterior_path(start, targets, blocked, limit=96):
    """Find a cardinal pedestrian connection avoiding entire building masks."""
    height, width = targets.shape
    x, y = start
    if not (0 <= x < width and 0 <= y < height) or blocked[y, x]:
        return []
    pending = deque([(x, y)])
    previous = {(x, y): None}
    distance = {(x, y): 0}
    while pending:
        x, y = point = pending.popleft()
        if targets[y, x]:
            path = []
            while point is not None:
                path.append(point)
                point = previous[point]
            return path[::-1]
        if distance[x, y] >= limit:
            continue
        for xx, yy in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if (0 <= xx < width and 0 <= yy < height and not blocked[yy, xx]
                    and (xx, yy) not in previous):
                previous[xx, yy] = (x, y)
                distance[xx, yy] = distance[x, y]+1
                pending.append((xx, yy))
    return []


def parking_stalls(rect, stall_width=4, stall_depth=7, aisle_width=8):
    """Yield divider polylines for parking banks with a real open drive aisle."""
    x, y, w, h = rect
    for top in range(y+4, y+h-stall_depth-3, 2*stall_depth+aisle_width):
        for left in range(x+4, x+w-4, stall_width):
            yield [(left, yy) for yy in range(top, top+stall_depth)]
            opposite = top+stall_depth+aisle_width
            if opposite+stall_depth < y+h-3:
                yield [(left, yy) for yy in range(opposite, opposite+stall_depth)]
