import pygame
from assets import load_assets, load_menu_textures
from main_menu import Menu
from game import init_game
from tickrate import TickRate
import settings
from game import init_game, run_game
from settings_menu import SettingsMenu

pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
tick = TickRate(settings.FPS)

icon, floor_tiles, wall_tiles, ladder = load_assets()
pygame.display.set_icon(icon)

btn_idle, btn_hover, btn_click = load_menu_textures()
menu = Menu(btn_idle, btn_hover, btn_click)

settings_menu = SettingsMenu()

state = "menu"
world, player = None, None#init_game(floor_tiles)

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
            if world is None:
                world, player = init_game(floor_tiles)
            state = "playing"
        elif result == "settings":
            # Create a fresh settings menu with current resolution
            settings_menu = SettingsMenu()
            state = "settings"
        elif result == "exit":
            running = False

    elif state == "settings":
        result = settings_menu.run(screen, events)
        if result == "back":
            state = "menu"
            tick = TickRate(settings.FPS)
            screen = pygame.display.get_surface()  # get the new surface after mode change
            # Rebuild menus with new dimensions
            menu = Menu(btn_idle, btn_hover, btn_click)

    elif state == "playing":
        result, world, player = run_game(screen, dt, events, world, player, floor_tiles, wall_tiles, ladder)
        state = result

    pygame.display.update()

pygame.quit()