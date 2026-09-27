import math
import random

#Creating dimmensions 
W, H = 64, 32
SOLID = {1, 2, 3, 4, 7}  # tile ids (mod 10) that block movement and placement

# Tile id -> base color. 0 = empty (sky/air), 5 = torch (drawn specially).
COLORS = {
    1: (122, 74, 43),    # dirt
    2: (104, 109, 120),  # stone
    3: (168, 116, 58),   # wood
    4: (164, 67, 47),    # brick
    6: (61, 139, 52),    # leaves
    7: (95, 100, 112),   # ore vein
}


def generate():
    """Builds a rolling-hills world with a couple of trees, same scheme as the web version:
    tiles >= 10 are player-placed (so breaking them refunds a block)."""
    world = [[0] * W for _ in range(H)]
    p1, p2 = random.random() * 6, random.random() * 6
    surface_y = []
    for x in range(W):
        sy = round(11 + 3 * math.sin(x * 0.18 + p1) + 2 * math.sin(x * 0.07 + p2))
        surface_y.append(sy)

    for y in range(H):
        for x in range(W):
            sy = surface_y[x]
            if y < sy:
                t = 0
            elif y < sy + 5:
                t = 1
            else:
                t = 2
                if y > sy + 8 and random.random() < 0.05:
                    t = 7
            world[y][x] = t

    x = 4
    while x < W - 4:
        sy = surface_y[x]
        h = random.randint(3, 4)
        for i in range(1, h + 1):
            if 0 <= sy - i < H:
                world[sy - i][x] = 3
        for dy in range(-2, 1):
            for dx in range(-1, 2):
                yy, xx = sy - h + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and not world[yy][xx]:
                    world[yy][xx] = 6
        x += random.randint(4, 7)

    return world


def solid(world, x, y):
    if x < 0 or x >= W:
        return True
    if y < 0:
        return False
    if y >= H:
        return True
    return world[y][x] % 10 in SOLID