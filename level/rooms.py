import random
from level.world import FLOOR


def create_room(world, x, y, w, h):
    for ry in range(y, y + h):
        for rx in range(x, x + w):
            world.tiles[ry][rx] = FLOOR


def connect_rooms(world, x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        world.tiles[y1][x] = FLOOR
    for y in range(min(y1, y2), max(y1, y2) + 1):
        world.tiles[y][x2] = FLOOR


def generate_rooms(world):
    w = len(world.tiles[0])
    h = len(world.tiles)

    rooms_centers = []
    rw, rh = 12, 12
    rx = w // 2 - rw // 2
    ry = h // 2 - rh // 2

    create_room(world, rx, ry, rw, rh)

    cx = rx + rw // 2
    cy = ry + rh // 2

    world.spawn_x = cx
    world.spawn_y = cy

    rooms_centers.append((cx, cy))
    for _ in range(20):
        rw = random.randint(5, 10)
        rh = random.randint(5, 10)

        rx = random.randint(1, w - rw - 2)
        ry = random.randint(1, h - rh - 2)

        create_room(world, rx, ry, rw, rh)

        cx = rx + rw // 2
        cy = ry + rh // 2

        connect_rooms(world, rooms_centers[-1][0], rooms_centers[-1][1], cx, cy)

        rooms_centers.append((cx, cy))