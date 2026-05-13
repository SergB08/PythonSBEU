import pygame
from assets import load_assets, load_menu_textures
from main_menu import Menu
from game import init_game
from tickrate import TickRate
import settings
from game import init_game, run_game

pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
tick = TickRate(settings.FPS)

icon, floor_tiles, wall_tiles = load_assets()
pygame.display.set_icon(icon)

btn_idle, btn_hover, btn_click = load_menu_textures()
menu = Menu(btn_idle, btn_hover, btn_click)

state = "menu"
world, player = None, None   # not loaded yet

running = True
while running:
    dt = tick.tick()
    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        events.append(event)

    screen.fill((0, 0, 0))

    if state == "menu":
        result = menu.run(screen, events)
        if result == "play":
            if world is None:          # generate only once on first Play
                world, player = init_game(floor_tiles)
            state = "playing"
        elif result == "settings":
            pass
        elif result == "exit":
            running = False

    elif state == "playing":
        run_game(screen, dt, events, world, player, floor_tiles, wall_tiles)

    pygame.display.update()

pygame.quit()