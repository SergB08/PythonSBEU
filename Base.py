import pygame

from entities.player import Player
from assets import load_assets, load_player_sprites
from tickrate import TickRate

from level.generation import generate_world
from level.rendering import draw_world

import settings

pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

tick = TickRate(settings.FPS)

icon, floor_tiles, wall_tiles = load_assets()
animations, idles = load_player_sprites()

pygame.display.set_icon(icon)

world = generate_world(settings.WORLD_WIDTH, settings.WORLD_HEIGHT, len(floor_tiles))

player = Player(animations, idles)

player.world_x = world.spawn_x * settings.TILE_SIZE
player.world_y = world.spawn_y * settings.TILE_SIZE

running = True

while running:

    dt = tick.tick()
    keys = pygame.key.get_pressed()

    player.update(keys, dt, world)

    camera_x = player.world_x - settings.WIDTH // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    screen.fill((0, 0, 0))

    draw_world(screen, world, floor_tiles, wall_tiles, camera_x, camera_y)

    player.draw(screen, keys)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()