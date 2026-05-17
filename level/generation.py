import random

from level.world import World, WALL, FLOOR
from level.rooms import generate_rooms


def generate_world(floor_count, level=1):
    world = World()
    world.level = level
    world.tiles = []
    world.floor_variant = []

    generate_rooms(world)

    for y in range(len(world.tiles)):
        for x in range(len(world.tiles[0])):
            world.floor_variant[y][x] = random.randint(0, floor_count - 1)

    if world.spawn_x == 0 and world.spawn_y == 0:
        world.spawn_x = len(world.tiles[0]) // 2
        world.spawn_y = len(world.tiles)    // 2

    return world


def generate_safe_room_world(floor_count):
    """
    Creates a single large room with no turrets and no ladder.
    Uses the same tile system as normal levels so the same
    floor/wall textures render identically.
    """
    import settings

    world = World()
    world.level = 0   # 0 = hub / safe room

    # Build a grid filled with walls
    room_size = 20          # tiles wide/tall for the safe room interior
    padding   = 3           # wall border
    total     = room_size + padding * 2

    world.tiles        = [[1] * total for _ in range(total)]
    world.floor_variant = [[0] * total for _ in range(total)]

    # Carve out the interior floor
    for y in range(padding, padding + room_size):
        for x in range(padding, padding + room_size):
            world.tiles[y][x] = FLOOR

    # Randomise floor variants
    for y in range(len(world.tiles)):
        for x in range(len(world.tiles[0])):
            world.floor_variant[y][x] = random.randint(0, max(0, floor_count - 1))

    # Spawn player in the centre
    world.spawn_x = total // 2
    world.spawn_y = total // 2

    # No turrets, no ladder in safe room
    world.turrets       = []
    world.turret_spawns = []
    world.ladder_x      = None
    world.ladder_y      = None

    world.width  = total
    world.height = total

    return world