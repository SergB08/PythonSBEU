# game.py
import pygame
import settings
from entities.player import Player
from assets import load_player_sprites2
from level.generation import generate_world
from level.rendering import draw_world, draw_minimap

def init_game(floor_tiles):
    animations, idles = load_player_sprites2()
    world = generate_world(settings.WORLD_WIDTH, settings.WORLD_HEIGHT, len(floor_tiles))
    player = Player(animations, idles)
    player.world_x = world.spawn_x * settings.TILE_SIZE
    player.world_y = world.spawn_y * settings.TILE_SIZE
    return world, player

def run_game(screen, dt, events, world, player, floor_tiles, wall_tiles):
    keys = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"   # back to menu later if you want
    player.update(keys, dt, world)
    camera_x = player.world_x - settings.WIDTH // 2
    camera_y = player.world_y - settings.HEIGHT // 2
    draw_world(screen, world, floor_tiles, wall_tiles, camera_x, camera_y)
    draw_minimap(screen, world, player)
    player.draw(screen, keys)
    dt_placeholder = None   # dt comes from Base.py, pass it in if needed
    return "playing"