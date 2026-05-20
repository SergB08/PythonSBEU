import random
import settings
from level.world import FLOOR
from entities.loot_item import LootItem

ROOM_SIZE = settings.ROOM_SIZE

def create_room(world, grid_x, grid_y, w=1, h=1):
    start_x = grid_x * ROOM_SIZE + 1
    start_y = grid_y * ROOM_SIZE + 1
    end_x = start_x + ROOM_SIZE * w - 2
    end_y = start_y + ROOM_SIZE * h - 2

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            world.tiles[y][x] = FLOOR

    center_x = start_x + (ROOM_SIZE * w) // 2 - 1
    center_y = start_y + (ROOM_SIZE * h) // 2 - 1

    return center_x, center_y


def connect_rooms(world, x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in range(-settings.CORRIDOR_WIDTH, settings.CORRIDOR_WIDTH + 1):
            if 0 <= y1 + dy < len(world.tiles):
                world.tiles[y1 + dy][x] = FLOOR

    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in range(-settings.CORRIDOR_WIDTH, settings.CORRIDOR_WIDTH + 1):
            if 0 <= y < len(world.tiles) and 0 <= x2 + dx < len(world.tiles[0]):
                world.tiles[y][x2 + dx] = FLOOR


def generate_rooms(world):
    grid_w = settings.GRID_WIDTH
    grid_h = settings.GRID_HEIGHT

    start_room = (grid_w // 2, grid_h // 2)
    room_positions = [start_room]
    taken = {start_room}

    room_count = random.randint(settings.ROOM_COUNT_MIN, settings.ROOM_COUNT_MAX)

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # Decide room sizes — 1x1, 1x2, or 2x2
    room_sizes = {}
    room_sizes[start_room] = (1, 1)

    while len(room_positions) < room_count:
        base = random.choice(room_positions)
        dx, dy = random.choice(directions)
        new_room = (base[0] + dx, base[1] + dy)

        if new_room in taken:
            continue
        if not (0 <= new_room[0] < grid_w and 0 <= new_room[1] < grid_h):
            continue

        # Pick random size
        size = random.choice([(1, 1), (1, 1), (1, 1), (1, 2), (2, 1), (2, 2)])

        # Make sure the extra tiles fit in the grid
        rw, rh = size
        if new_room[0] + rw > grid_w or new_room[1] + rh > grid_h:
            size = (1, 1)
            rw, rh = 1, 1

        # Mark all grid cells as taken
        fits = True
        cells = []
        for ox in range(rw):
            for oy in range(rh):
                cell = (new_room[0] + ox, new_room[1] + oy)
                if cell in taken:
                    fits = False
                    break
                cells.append(cell)

        if not fits:
            continue

        for cell in cells:
            taken.add(cell)

        room_positions.append(new_room)
        room_sizes[new_room] = size

    # Rebuild world tiles to match grid size
    world.width  = grid_w * ROOM_SIZE + 2
    world.height = grid_h * ROOM_SIZE + 2
    world.tiles        = [[1] * world.width  for _ in range(world.height)]
    world.floor_variant = [[0] * world.width for _ in range(world.height)]

    centers = []
    for room in room_positions:
        rw, rh = room_sizes.get(room, (1, 1))
        cx, cy = create_room(world, room[0], room[1], rw, rh)
        centers.append((cx, cy))

    for i in range(1, len(centers)):
        connect_rooms(world, centers[i-1][0], centers[i-1][1],
                             centers[i][0],   centers[i][1])

    world.rooms = centers
    world.spawn_x = centers[0][0]
    world.spawn_y = centers[0][1]

    final_room = centers[-1]
    world.ladder_x = final_room[0]
    world.ladder_y = final_room[1]

    turret_spawn_tiles = []
    for i, (cx, cy) in enumerate(centers):
        if i == 0:
            continue
        rw, rh = room_sizes.get(room_positions[i], (1, 1))
        room_area = rw * rh
        if room_area == 1:
            count = 1
        elif room_area == 2:
            count = random.randint(1, 2)
        else:  # 2x2
            count = random.randint(2, 3)
        for _ in range(count):
            turret_spawn_tiles.append((cx, cy))

    world.turret_spawns = turret_spawn_tiles

    # ── Loot spawns ──────────────────────────────────────────────────────
    # Each room gets loot slots proportional to its area.
    # room_index 0 = spawn room (no loot there)
       # ── Loot spawns ──────────────────────────────────────────────────────
    from ui.inventoryui import make_medkit, make_bandage, make_ammo_pistol
    from entities.loot_item import LootItem
    import random as _r

    LOOT_TABLE = [
        (make_medkit,                    0.25),
        (make_bandage,                   0.25),
        (lambda: make_ammo_pistol(10),   0.75),
    ]

    world.loot_items = []   # List of LootItem objects

    for i, (cx, cy) in enumerate(centers):
        if i == 0:
            continue

        rw, rh = room_sizes.get(room_positions[i], (1, 1))
        room_area   = rw * rh
        max_items   = {1: 2, 2: 3, 4: 5}.get(room_area, 2)

        half_w = (ROOM_SIZE * rw) // 2 - 2
        half_h = (ROOM_SIZE * rh) // 2 - 2

        placed = 0
        attempts = 0
        used_positions = set()

        while placed < max_items and attempts < 60:
            attempts += 1

            ox = _r.randint(-half_w, half_w)
            oy = _r.randint(-half_h, half_h)
            tx = cx + ox
            ty = cy + oy

            if (tx, ty) in used_positions:
                continue
            if not (0 <= ty < len(world.tiles) and 0 <= tx < len(world.tiles[0])):
                continue
            if world.tiles[ty][tx] != FLOOR:
                continue

            roll = _r.random()
            cumulative = 0.0
            chosen_factory = None
            for factory, chance in LOOT_TABLE:
                cumulative += chance
                if roll < cumulative:
                    chosen_factory = factory
                    break

            if chosen_factory is None:
                placed += 1
                used_positions.add((tx, ty))
                continue

            used_positions.add((tx, ty))
            # Create actual LootItem at world coordinates
            world_x = tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
            world_y = ty * settings.TILE_SIZE + settings.TILE_SIZE // 2
            world.loot_items.append(LootItem(world_x, world_y, chosen_factory()))
            placed += 1