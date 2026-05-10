from level.world import World, WALL
from level.rooms import generate_rooms


def generate_world(width, height, floor_count):
    world = World()
    for y in range(height):
        row = []
        floor_row = []

        for x in range(width):
            row.append(WALL)
            floor_row.append(0)

        world.tiles.append(row)
        world.floor_variant.append(floor_row)

    generate_rooms(world)

    return world