import pygame
from assets import load_assets, load_menu_textures
from main_menu import Menu
from game import init_game, init_safe_room, run_game, run_safe_room
from tickrate import TickRate
import settings
from settings_menu import SettingsMenu

# ініціалізація pygame та мікшера
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=16, buffer=512)
pygame.mixer.set_num_channels(16)  # збільшуємо кількість каналів з 8 до 16
pygame.mouse.set_visible(False)    # ховаємо курсор ОС

#створення вікна та таймера
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
tick   = TickRate(settings.FPS)

#завантаження ресурсів
icon, floor_tiles, wall_tiles, ladder = load_assets()
pygame.display.set_icon(icon)

#ініціалізація меню
btn_idle, btn_hover, btn_click = load_menu_textures()
menu          = Menu(btn_idle, btn_hover, btn_click)
settings_menu = SettingsMenu()

#початковий стан гри
world, player, safe_room = init_safe_room(floor_tiles)
state = "menu"  # поточний стан: menu | settings | safe_room | playing

#головний цикл гри
running = True
while running:
    dt     = tick.tick()   # дельта-час у секундах
    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        events.append(event)

    screen.fill((0, 0, 0))  # очищення екрану

    if state == "menu":
        pygame.mouse.set_visible(True)   # показуємо курсор у меню
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
            # перестворюємо таймер та меню після зміни налаштувань
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
        # якщо повернулись у меню то скидаємо стан безпечної кімнати
        if state == "menu":
            world, player, safe_room = init_safe_room(floor_tiles)

    elif state == "playing":
        pygame.mouse.set_visible(False)
        result, world, player, safe_room = run_game(
            screen, dt, events, world, player,
            floor_tiles, wall_tiles, ladder, safe_room
        )
        state = result
        # якщо повернулись у меню — скидаємо стан гри
        if state == "menu":
            world, player, safe_room = init_safe_room(floor_tiles)

    pygame.display.update()  # оновлення екрану

pygame.quit()