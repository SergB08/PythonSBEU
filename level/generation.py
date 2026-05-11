import random
from level.world import World, WALL, FLOOR
from level.rooms import generate_rooms


def generate_world(width, height, floor_count):

    world = World()

    # ===== 1. створення базового світу =====

    for y in range(height):

        row = []
        floor_row = []

        for x in range(width):

            row.append(WALL)

            floor_row.append(
                random.randint(
                    0,
                    floor_count - 1
                )
            )

        world.tiles.append(row)
        world.floor_variant.append(floor_row)

    # ===== 2. генерація кімнат =====

    generate_rooms(world)

    # ===== 3. SPAWN =====
    # spawn вже записується в rooms.py

    # але гарантія (на випадок багів)
    if world.spawn_x == 0 and world.spawn_y == 0:

        world.spawn_x = width // 2
        world.spawn_y = height // 2

    return world