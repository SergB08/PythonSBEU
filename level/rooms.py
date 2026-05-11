import random
from level.world import FLOOR

ROOM_SIZE = 12


def create_room(world, grid_x, grid_y):

    start_x = grid_x * ROOM_SIZE + 1
    start_y = grid_y * ROOM_SIZE + 1

    for y in range(start_y, start_y + ROOM_SIZE - 2):
        for x in range(start_x, start_x + ROOM_SIZE - 2):

            world.tiles[y][x] = FLOOR

    center_x = start_x + ROOM_SIZE // 2 - 1
    center_y = start_y + ROOM_SIZE // 2 - 1

    return center_x, center_y


def connect_rooms(world, x1, y1, x2, y2):

    for x in range(min(x1, x2), max(x1, x2) + 1):
        world.tiles[y1][x] = FLOOR

    for y in range(min(y1, y2), max(y1, y2) + 1):
        world.tiles[y][x2] = FLOOR


def generate_rooms(world):

    grid_w = 5
    grid_h = 5

    start_room = (2, 2)

    room_positions = [start_room]
    taken = {start_room}

    room_count = min(3 + world.level, 8)

    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    while len(room_positions) < room_count:

        base = random.choice(room_positions)

        dx, dy = random.choice(directions)

        new_room = (
            base[0] + dx,
            base[1] + dy
        )

        if new_room in taken:
            continue

        if not (0 <= new_room[0] < grid_w and 0 <= new_room[1] < grid_h):
            continue

        room_positions.append(new_room)
        taken.add(new_room)

    centers = []

    for room in room_positions:

        cx, cy = create_room(
            world,
            room[0],
            room[1]
        )

        centers.append((cx, cy))

    for i in range(1, len(centers)):

        connect_rooms(
            world,
            centers[i - 1][0],
            centers[i - 1][1],
            centers[i][0],
            centers[i][1]
        )

    world.rooms = centers

    world.spawn_x = centers[0][0]
    world.spawn_y = centers[0][1]

    final_room = centers[-1]

    world.ladder_x = final_room[0]
    world.ladder_y = final_room[1]