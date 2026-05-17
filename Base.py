import pygame
from assets import load_assets, load_menu_textures
from main_menu import Menu
from game import init_game, init_safe_room, run_game, run_safe_room
from tickrate import TickRate
import settings
from settings_menu import SettingsMenu

pygame.init()
pygame.mouse.set_visible(False)   # hide OS cursor — crosshair drawn in-game

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
tick   = TickRate(settings.FPS)

icon, floor_tiles, wall_tiles, ladder = load_assets()
pygame.display.set_icon(icon)

btn_idle, btn_hover, btn_click = load_menu_textures()
menu          = Menu(btn_idle, btn_hover, btn_click)
settings_menu = SettingsMenu()

world, player, safe_room = init_safe_room(floor_tiles)

state = "menu"

running = True
while running:
    dt     = tick.tick()
    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        events.append(event)

    screen.fill((0, 0, 0))

    if state == "menu":
        pygame.mouse.set_visible(True)   # show cursor in menu
        result = menu.run(screen, events)
        if result == "play":
            pygame.mouse.set_visible(False)
            world, player, safe_room = init_safe_room(floor_tiles)
            state = "safe_room"
        elif result == "settings":
            settings_menu = SettingsMenu()
            state = "settings"
        elif result == "exit":
            running = False

    elif state == "settings":
        result = settings_menu.run(screen, events)
        if result == "back":
            state  = "menu"
            tick   = TickRate(settings.FPS)
            screen = pygame.display.get_surface()
            menu   = Menu(btn_idle, btn_hover, btn_click)

    elif state == "safe_room":
        pygame.mouse.set_visible(False)
        state, world, player, safe_room = run_safe_room(
            screen, dt, events, world, player, safe_room,
            floor_tiles, wall_tiles, ladder
        )
        if state == "menu":
            world, player, safe_room = init_safe_room(floor_tiles)

    elif state == "playing":
        pygame.mouse.set_visible(False)
        result, world, player, safe_room = run_game(
            screen, dt, events, world, player,
            floor_tiles, wall_tiles, ladder, safe_room
        )
        state = result
        if state == "menu":
            world, player, safe_room = init_safe_room(floor_tiles)

    pygame.display.update()

pygame.quit()