import random
import settings
from level.world import FLOOR, WALL


def draw_world(screen, world, floor_tiles, wall_tiles, camera_x, camera_y):

    for y, row in enumerate(world.tiles):
        for x, tile in enumerate(row):

            draw_x = x * settings.TILE_SIZE - camera_x
            draw_y = y * settings.TILE_SIZE - camera_y

            if draw_x < -settings.TILE_SIZE or draw_x > settings.WIDTH or draw_y < -settings.TILE_SIZE or draw_y > settings.HEIGHT:
                continue

            if tile == FLOOR:
                img = floor_tiles[world.floor_variant[y][x] % len(floor_tiles)]
                screen.blit(img, (draw_x, draw_y))

            elif tile == WALL:
                img = wall_tiles[0]
                screen.blit(img, (draw_x, draw_y))