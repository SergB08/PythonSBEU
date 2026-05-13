import random

from level.world import World, WALL
from level.rooms import generate_rooms


def generate_world(floor_count, level=1):
    world = World()
    world.level = level
    world.tiles = []
    world.floor_variant = []

    generate_rooms(world)

    # Fill floor_variant with random values
    import random
    for y in range(len(world.tiles)):
        for x in range(len(world.tiles[0])):
            world.floor_variant[y][x] = random.randint(0, floor_count - 1)

    if world.spawn_x == 0 and world.spawn_y == 0:
        world.spawn_x = len(world.tiles[0]) // 2
        world.spawn_y = len(world.tiles)    // 2

    return world