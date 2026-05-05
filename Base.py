import pygame
import settings
from entities.player import Player
from assets import load_assets, load_player_sprites
from tickrate import TickRate
from levelGenerator import build_tilemap


pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), flags=pygame.NOFRAME)
tickrate = TickRate(settings.FPS)
#icon, bg = load_assets()
bg = load_assets()
#animations, idles = load_player_sprites()
anim_player_walk, anim_player_idle = load_player_sprites()
#pygame.display.set_icon(icon)

#player = Player(animations, idles)
player = Player(anim_player_walk, anim_player_idle)

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