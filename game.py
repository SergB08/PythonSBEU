# game.py
import pygame
import settings
import controls
from entities.player import Player, draw_crosshair
from assets import load_player_sprites2
from level.generation import generate_world, generate_safe_room_world
from level.rendering import draw_world, draw_minimap
from assets import load_player_sprites2, load_turret_sprites
from level.safe_room import SafeRoom

from death_screen import DeathScreen

_death_screen = None   # lazy singleton


def init_game(floor_tiles):
    animations, idles = load_player_sprites2()
    world  = generate_world(len(floor_tiles))
    player = Player(animations, idles)
    player.world_x = world.spawn_x * settings.TILE_SIZE
    player.world_y = world.spawn_y * settings.TILE_SIZE

    legs, head_calm, head_angry = load_turret_sprites()
    world.turrets = []
    for tx, ty in world.turret_spawns:
        from entities.turret import Turret
        world.turrets.append(Turret(
            tx * settings.TILE_SIZE,
            ty * settings.TILE_SIZE,
            legs, head_calm, head_angry
        ))

    return world, player


def init_safe_room(floor_tiles, existing_player=None):
    animations, idles = load_player_sprites2()
    world = generate_safe_room_world(len(floor_tiles))

    if existing_player is None:
        player = Player(animations, idles)
    else:
        player = existing_player
        player.bullets = []

    player.world_x = world.spawn_x * settings.TILE_SIZE
    player.world_y = world.spawn_y * settings.TILE_SIZE

    safe_room = SafeRoom(world)
    return world, player, safe_room


def run_safe_room(screen, dt, events, world, player, safe_room,
                  floor_tiles, wall_tiles, ladder_img):
    keys = pygame.key.get_pressed()

    camera_x = player.world_x - settings.WIDTH  // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
    draw_minimap(screen, world, player)

    result = safe_room.update(dt, player, events)
    safe_room.draw(screen, camera_x, camera_y, player)

    player.update(keys, dt, world, pygame.mouse.get_pressed(), events)
    player.draw(screen, keys)
    player.draw_bullets(screen, camera_x, camera_y)
    player.draw_hud(screen)

    draw_crosshair(screen)

    font = pygame.font.SysFont(None, 40, bold=True)
    lbl  = font.render("SAFE ROOM", True, (150, 220, 255))
    screen.blit(lbl, (settings.WIDTH // 2 - lbl.get_width() // 2, 30))

    if result == "enter_level":
        new_world, new_player = init_game(floor_tiles)
        new_world.level = 1
        new_player.hp   = player.hp
        return "playing", new_world, new_player, safe_room

    return "safe_room", world, player, safe_room


def run_game(screen, dt, events, world, player, floor_tiles, wall_tiles, ladder_img,
             safe_room=None):
    keys          = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    near_ladder         = False
    near_ladder_blocked = False
    all_turrets_dead    = all(not t.alive for t in world.turrets)

    if world.ladder_x is not None:
        dx = player.world_x - (world.ladder_x * settings.TILE_SIZE + settings.TILE_SIZE * 2)
        dy = player.world_y - (world.ladder_y * settings.TILE_SIZE + settings.TILE_SIZE * 2)
        close = abs(dx) < settings.TILE_SIZE * 2 and abs(dy) < settings.TILE_SIZE * 2
        near_ladder         = close and all_turrets_dead
        near_ladder_blocked = close and not all_turrets_dead

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu", world, player, safe_room
            if event.key == controls.INTERACT_KEY and near_ladder:
                next_level = world.level + 1
                new_world, new_player = init_game(floor_tiles)
                new_world.level = next_level
                new_player.hp   = player.hp
                new_player.ammo = player.ammo
                return "playing", new_world, new_player, safe_room

    player.update(keys, dt, world, mouse_buttons, events)

    camera_x = player.world_x - settings.WIDTH  // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
    draw_minimap(screen, world, player)
    player.draw(screen, keys)
    player.draw_bullets(screen, camera_x, camera_y)

    if near_ladder_blocked:
        font = pygame.font.SysFont(None, 40, bold=True)
        text = font.render("Eliminate all enemies first!", True, (255, 80, 80))
        screen.blit(text, (settings.WIDTH  // 2 - text.get_width()  // 2,
                            settings.HEIGHT // 2 - 100))

    if near_ladder:
        font = pygame.font.SysFont(None, 40, bold=True)
        text = font.render("[E] Enter next level", True, (100, 255, 120))
        screen.blit(text, (settings.WIDTH  // 2 - text.get_width()  // 2,
                            settings.HEIGHT // 2 - 100))

    for turret in world.turrets:
        turret.update(dt, player, world)
        turret.draw(screen, camera_x, camera_y)

        for bullet in turret.bullets:
            if bullet.alive:
                dx = bullet.x - player.world_x
                dy = bullet.y - player.world_y
                if abs(dx) < 30 and abs(dy) < 30:
                    player.take_damage(bullet.DAMAGE)
                    bullet.alive = False

        for bullet in player.bullets:
            if bullet.alive:
                dx = bullet.x - turret.world_x
                dy = bullet.y - turret.world_y
                if abs(dx) < 60 and abs(dy) < 60:
                    turret.take_damage(bullet.DAMAGE, camera_x, camera_y)
                    bullet.alive = False

    player.draw_hud(screen)
    draw_crosshair(screen)

    if not player.alive:
        global _death_screen
        if _death_screen is None:
            _death_screen = DeathScreen()
        result = _death_screen.run(screen, events)
        if result == "restart":
            new_world, new_player = init_game(floor_tiles)
            return "playing", new_world, new_player, safe_room
        if result == "menu":
            return "menu", None, None, None

    return "playing", world, player, safe_room