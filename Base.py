import pygame
from entities.player import Player

from assets import load_assets,load_map_textures , load_player_sprites

from levelGenerator import generate_level, build_tilemap, TILE_SIZE, WIDTH, HEIGHT, FLOOR_TEXTURE_PATH, WALL_TEXTURE_PATH

from tickrate import TickRate
import settings

pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), flags=pygame.NOFRAME)
tickrate = TickRate(settings.FPS)
icon, bg = load_assets()
animations, idles = load_player_sprites()
pygame.display.set_icon(icon)

# Player
player = Player(anim_player_idle, anim_player_walk)

bg_x = 0
bg_y = 0

running = True

while running:
    dt = tickrate.tick()
    
    screen.blit(bg, (bg_x, bg_y))
    keys = pygame.key.get_pressed()
    moving = player.update(keys, dt)
    player.draw(screen, keys)

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
    
pygame.quit()