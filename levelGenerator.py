import pygame
import random

# Папки з текстурами
FLOOR_TEXTURE_PATH = "textures/floor"
WALL_TEXTURE_PATH = "textures/walls"

TILE_SIZE = 64

# Розмір мапи (у тайлах)
MAP_WIDTH = 50
MAP_HEIGHT = 30


def load_textures():
    """Завантажує випадкові текстури підлоги та стін"""
    floor_tiles = []
    wall_tiles = []

    # завантаження підлоги
    for i in range(1, 5):  # floor1.png ... floor4.png
        img = pygame.image.load(f"{FLOOR_TEXTURE_PATH}/kafel{i}.png").convert()
        floor_tiles.append(img)

    # завантаження стін
    for i in range(1, 5):  # wall1.png ... wall4.png
        img = pygame.image.load(f"{WALL_TEXTURE_PATH}/testWall.png").convert_alpha()
        wall_tiles.append(img)

    return floor_tiles, wall_tiles


def generate_map():
    """
    Створює просту карту:
    0 = підлога
    1 = стіна
    """
    tilemap = []

    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):

            # рамка = стіни
            if x == 0 or y == 0 or x == MAP_WIDTH - 1 or y == MAP_HEIGHT - 1:
                row.append(1)
            else:
                # випадкові внутрішні стіни (5% шанс)
                row.append(1 if random.random() < 0.05 else 0)

        tilemap.append(row)

    return tilemap


def build_tilemap():
    """Головна функція для гри"""
    floor_tiles, wall_tiles = load_textures()
    tilemap = generate_map()

    return tilemap, floor_tiles, wall_tiles


def draw_tilemap(screen, tilemap, floor_tiles, wall_tiles, camera_x=0, camera_y=0):
    """Рендер карти"""
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):

            screen_x = x * TILE_SIZE - camera_x
            screen_y = y * TILE_SIZE - camera_y

            if tile == 0:
                img = random.choice(floor_tiles)
            else:
                img = random.choice(wall_tiles)

            screen.blit(img, (screen_x, screen_y))