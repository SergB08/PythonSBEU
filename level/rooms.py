import random
import settings
from level.world import FLOOR
from entities.loot_item import LootItem

ROOM_SIZE = settings.ROOM_SIZE  # розмір кімнати в тайлах


def create_room(world, grid_x, grid_y, w=1, h=1):
    #Заповнює прямокутну область тайлами підлоги. Повертає центр кімнати в тайлових координатах
    start_x = grid_x * ROOM_SIZE + 1
    start_y = grid_y * ROOM_SIZE + 1
    end_x = start_x + ROOM_SIZE * w - 2
    end_y = start_y + ROOM_SIZE * h - 2

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            world.tiles[y][x] = FLOOR

    # розраховує центр кімнати
    center_x = start_x + (ROOM_SIZE * w) // 2 - 1
    center_y = start_y + (ROOM_SIZE * h) // 2 - 1

    return center_x, center_y


def connect_rooms(world, x1, y1, x2, y2):
    #З'єднує дві кімнати Г-подібним коридором через точки (x1,y1) та (x2,y2)
    # горизонтальна частина коридору
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in range(-settings.CORRIDOR_WIDTH, settings.CORRIDOR_WIDTH + 1):
            if 0 <= y1 + dy < len(world.tiles):
                world.tiles[y1 + dy][x] = FLOOR

    # вертикальна частина коридору
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in range(-settings.CORRIDOR_WIDTH, settings.CORRIDOR_WIDTH + 1):
            if 0 <= y < len(world.tiles) and 0 <= x2 + dx < len(world.tiles[0]):
                world.tiles[y][x2 + dx] = FLOOR


def generate_rooms(world):
    #Генерує всі кімнати, коридори, спавни турелей та предмети лута для рівня
    grid_w = settings.GRID_WIDTH
    grid_h = settings.GRID_HEIGHT

    # починаємо з центральної клітинки сітки
    start_room = (grid_w // 2, grid_h // 2)
    room_positions = [start_room]
    taken = {start_room}  # зайняті клітинки сітки

    room_count = random.randint(settings.ROOM_COUNT_MIN, settings.ROOM_COUNT_MAX)

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # можливі напрямки розширення

    # визначаємо розміри кімнат 1x1, 1x2 або 2x2
    room_sizes = {}
    room_sizes[start_room] = (1, 1)

    while len(room_positions) < room_count:
        base = random.choice(room_positions)
        dx, dy = random.choice(directions)
        new_room = (base[0] + dx, base[1] + dy)

        # пропускаємо якщо зайнято або виходить за межі
        if new_room in taken:
            continue
        if not (0 <= new_room[0] < grid_w and 0 <= new_room[1] < grid_h):
            continue

        # обираємо випадковий розмір кімнати
        size = random.choice([(1, 1), (1, 1), (1, 1), (1, 2), (2, 1), (2, 2)])

        # зменшуємо до 1x1 якщо не вміщується в сітку
        rw, rh = size
        if new_room[0] + rw > grid_w or new_room[1] + rh > grid_h:
            size = (1, 1)
            rw, rh = 1, 1

        # перевіряємо чи всі клітинки вільні
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

        # позначаємо клітинки як зайняті
        for cell in cells:
            taken.add(cell)

        room_positions.append(new_room)
        room_sizes[new_room] = size

    # перебудовуємо тайловий масив під розмір сітки
    world.width  = grid_w * ROOM_SIZE + 2
    world.height = grid_h * ROOM_SIZE + 2
    world.tiles        = [[1] * world.width  for _ in range(world.height)]
    world.floor_variant = [[0] * world.width for _ in range(world.height)]

    # створюємо кімнати та збираємо їх центри
    centers = []
    for room in room_positions:
        rw, rh = room_sizes.get(room, (1, 1))
        cx, cy = create_room(world, room[0], room[1], rw, rh)
        centers.append((cx, cy))

    # з'єднуємо кімнати послідовно коридорами
    for i in range(1, len(centers)):
        connect_rooms(world, centers[i-1][0], centers[i-1][1],
                             centers[i][0],   centers[i][1])

    # перша кімната — спавн гравця
    world.rooms = centers
    world.spawn_x = centers[0][0]
    world.spawn_y = centers[0][1]

    # остання кімната — вихід з рівня
    final_room = centers[-1]
    world.ladder_x = final_room[0]
    world.ladder_y = final_room[1]

    #Спавн турелей
    # кількість турелей залежить від площі кімнати
    turret_spawn_tiles = []
    for i, (cx, cy) in enumerate(centers):
        if i == 0:
            continue  # у стартовій кімнаті турелей немає
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

    # Спавн лута
    # кожна кімната (крім стартової) отримує предмети пропорційно до площі
    from ui.inventoryui import make_medkit, make_bandage, make_ammo_pistol
    from entities.loot_item import LootItem
    import random as _r

    # таблиця лута: (фабрика предмету, шанс випадіння)
    LOOT_TABLE = [
        (make_medkit,                    0.25),
        (make_bandage,                   0.25),
        (lambda: make_ammo_pistol(10),   0.75),
    ]

    world.loot_items = []  # список предметів що лежать на підлозі

    for i, (cx, cy) in enumerate(centers):
        if i == 0:
            continue  # у стартовій кімнаті лута немає

        rw, rh = room_sizes.get(room_positions[i], (1, 1))
        room_area = rw * rh
        max_items = {1: 2, 2: 3, 4: 5}.get(room_area, 2)  # максимум предметів за площею

        # межі для випадкового розміщення всередині кімнати
        half_w = (ROOM_SIZE * rw) // 2 - 2
        half_h = (ROOM_SIZE * rh) // 2 - 2

        placed = 0
        attempts = 0
        used_positions = set()  # вже зайняті позиції щоб не накладались

        while placed < max_items and attempts < 60:
            attempts += 1

            # випадкове зміщення від центру кімнати
            ox = _r.randint(-half_w, half_w)
            oy = _r.randint(-half_h, half_h)
            tx = cx + ox
            ty = cy + oy

            # пропускаємо зайняті або недійсні позиції
            if (tx, ty) in used_positions:
                continue
            if not (0 <= ty < len(world.tiles) and 0 <= tx < len(world.tiles[0])):
                continue
            if world.tiles[ty][tx] != FLOOR:
                continue

            # зважений випадковий вибір предмету з таблиці лута
            roll = _r.random()
            cumulative = 0.0
            chosen_factory = None
            for factory, chance in LOOT_TABLE:
                cumulative += chance
                if roll < cumulative:
                    chosen_factory = factory
                    break

            # якщо нічого не вибрано — пропускаємо слот
            if chosen_factory is None:
                placed += 1
                used_positions.add((tx, ty))
                continue

            used_positions.add((tx, ty))
            # створюємо предмет у світових координатах (центр тайлу)
            world_x = tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
            world_y = ty * settings.TILE_SIZE + settings.TILE_SIZE // 2
            world.loot_items.append(LootItem(world_x, world_y, chosen_factory()))
            placed += 1