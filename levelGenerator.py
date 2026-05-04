import pygame
import random
import os

# =========================
# CONFIG
# =========================

WIDTH = 80
HEIGHT = 50
TILE_SIZE = 16

# 👉 SET YOUR TEXTURE FOLDERS HERE
FLOOR_TEXTURE_PATH = "textures/floor"
WALL_TEXTURE_PATH = "textures/walls"

SCREEN_WIDTH = WIDTH * TILE_SIZE
SCREEN_HEIGHT = HEIGHT * TILE_SIZE

# Tile types
WALL = 0
FLOOR = 1
ROOM = 2

# =========================
# LOAD TEXTURES
# =========================

def load_textures(folder):
    textures = []
    if not os.path.exists(folder):
        print(f"Missing folder: {folder}")
        return textures

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            textures.append(img)
        except:
            pass

    return textures


# =========================
# GENERATION FUNCTIONS
# =========================

def create_grid():
    return [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]


def carve_room(grid, cx, cy, w, h):
    tiles = []
    for y in range(cy - h//2, cy + h//2):
        for x in range(cx - w//2, cx + w//2):
            if 1 <= x < WIDTH-1 and 1 <= y < HEIGHT-1:
                grid[y][x] = ROOM
                tiles.append((x, y))
    return tiles


def carve_corridor_path(grid, start_x, start_y, length):
    x, y = start_x, start_y
    path = [(x, y)]

    direction = (1, 0)

    for _ in range(length):
        if random.random() < 0.3:
            direction = random.choice([(1,0), (0,1), (0,-1)])

        x += direction[0]
        y += direction[1]

        x = max(2, min(WIDTH-3, x))
        y = max(2, min(HEIGHT-3, y))

        grid[y][x] = FLOOR
        path.append((x, y))

    return path


def try_place_room(grid, x, y):
    w = random.randint(4, 10)
    h = random.randint(4, 8)

    offset_x = random.randint(-2, 2)
    offset_y = random.randint(-2, 2)

    return carve_room(grid, x + offset_x, y + offset_y, w, h)


def connect_rooms(grid, room_a, room_b):
    (x1, y1) = random.choice(room_a)
    (x2, y2) = random.choice(room_b)

    x, y = x1, y1

    while x != x2:
        x += 1 if x2 > x else -1
        grid[y][x] = FLOOR

    while y != y2:
        y += 1 if y2 > y else -1
        grid[y][x] = FLOOR


# =========================
# TILEMAP BUILD
# =========================

def build_tilemap(grid, floor_tiles, wall_tiles):
    tilemap = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] in (FLOOR, ROOM):
                if floor_tiles:
                    tilemap[y][x] = random.choice(floor_tiles)
            else:
                if wall_tiles:
                    tilemap[y][x] = random.choice(wall_tiles)

    return tilemap


# =========================
# MAIN GENERATION
# =========================

def generate_level():
    grid = create_grid()

    # Start room
    start_room = carve_room(grid, 6, HEIGHT//2, 8, 6)

    # Corridor
    corridor = carve_corridor_path(grid, 6, HEIGHT//2, length=120)

    # Rooms
    rooms = []
    for (x, y) in corridor:
        if random.random() < 0.2:
            room = try_place_room(grid, x, y)
            rooms.append(room)

    # Optional connections
    for i in range(len(rooms)-1):
        if random.random() < 0.3:
            connect_rooms(grid, rooms[i], rooms[i+1])

    return grid, rooms


# =========================
# MAIN
# =========================

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

floor_tiles = load_textures(FLOOR_TEXTURE_PATH)
wall_tiles = load_textures(WALL_TEXTURE_PATH)

grid, rooms = generate_level()
tilemap = build_tilemap(grid, floor_tiles, wall_tiles)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Press R to regenerate level
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                grid, rooms = generate_level()
                tilemap = build_tilemap(grid, floor_tiles, wall_tiles)

    screen.fill((0, 0, 0))

    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = tilemap[y][x]
            if tile:
                screen.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
