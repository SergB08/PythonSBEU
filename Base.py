import pygame
import random

from entities.player import Player
from entities.turret import Turret
from assets import (
    load_assets,
    load_player_sprites,
    load_player_sprites2,
    load_turret_sprites,
)
from tickrate import TickRate

from level.generation import generate_world
from level.rendering import draw_world, draw_minimap

import settings

pygame.init()

# ===== ASSETS =====

ladder_img = pygame.image.load("textures/drabina.png")
ladder_img = pygame.transform.scale(ladder_img, (settings.TILE_SIZE, settings.TILE_SIZE))

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
tick = TickRate(settings.FPS)

icon, floor_tiles, wall_tiles = load_assets()
animations, idles = load_player_sprites()           # legacy – keep for now
playerIdle, playerWalk = load_player_sprites2()
turret_legs, turret_head_calm, turret_head_angry = load_turret_sprites()

pygame.display.set_icon(icon)


# ===== HELPERS =====

def spawn_turrets(world):
    """Create Turret objects from world.turret_spawns."""
    turrets = []
    for (tx, ty) in world.turret_spawns:
        wx = tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
        wy = ty * settings.TILE_SIZE + settings.TILE_SIZE // 2
        t = Turret(wx, wy, turret_legs, turret_head_calm, turret_head_angry)
        turrets.append(t)
    return turrets


def next_level(world, player):
    """Generate the next level and reset player position."""
    new_world = generate_world(
        settings.WORLD_WIDTH,
        settings.WORLD_HEIGHT,
        len(floor_tiles),
        world.level + 1
    )
    player.world_x = new_world.spawn_x * settings.TILE_SIZE
    player.world_y = new_world.spawn_y * settings.TILE_SIZE
    return new_world, spawn_turrets(new_world)


def check_bullet_hits(player, turrets, camera_x, camera_y):
    """
    Check player bullets vs turrets and turret bullets vs player.
    camera_x/y are needed so damage numbers spawn at the right screen position.
    """
    # Player bullets → turrets
    for turret in turrets:
        if not turret.alive:
            continue
        for bullet in player.bullets:
            if not bullet.alive:
                continue
            dx = bullet.x - turret.world_x
            dy = bullet.y - turret.world_y
            if abs(dx) < 40 and abs(dy) < 40:
                turret.take_damage(bullet.DAMAGE, camera_x, camera_y)
                bullet.alive = False

    # Turret bullets → player
    for turret in turrets:
        for bullet in turret.bullets:
            if not bullet.alive:
                continue
            dx = bullet.x - player.world_x
            dy = bullet.y - player.world_y
            if abs(dx) < 40 and abs(dy) < 40:
                player.take_damage(bullet.DAMAGE)
                bullet.alive = False


# ===== WORLD INIT =====

world = generate_world(settings.WORLD_WIDTH, settings.WORLD_HEIGHT, len(floor_tiles))
turrets = spawn_turrets(world)

player = Player(playerIdle, playerWalk)
player.world_x = world.spawn_x * settings.TILE_SIZE
player.world_y = world.spawn_y * settings.TILE_SIZE

# ===== GAME OVER FONT =====
font_big = pygame.font.SysFont(None, 80)

running = True

while running:

    dt = tick.tick()
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    # ===== UPDATE =====

    if player.alive:
        player.update(keys, dt, world, mouse_buttons)

    for turret in turrets:
        turret.update(dt, player, world)

    # Remove dead turrets
    turrets = [t for t in turrets if t.alive]

    # ===== CAMERA =====

    camera_x = player.world_x - settings.WIDTH // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    # Bullet collision
    if player.alive:
        check_bullet_hits(player, turrets, camera_x, camera_y)

    # ===== LADDER CHECK =====

    ladder_world_x = world.ladder_x * settings.TILE_SIZE
    ladder_world_y = world.ladder_y * settings.TILE_SIZE

    distance_x = abs(player.world_x - ladder_world_x)
    distance_y = abs(player.world_y - ladder_world_y)

    if player.alive and distance_x < 100 and distance_y < 100:
        if keys[pygame.K_e]:
            world, turrets = next_level(world, player)

    # ===== DRAW =====

    screen.fill((0, 0, 0))

    draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
    draw_minimap(screen, world, player)

    # Turrets (includes their bullets)
    for turret in turrets:
        turret.draw(screen, camera_x, camera_y)

    # Player sprite
    player.draw(screen, keys)

    # Player bullets
    player.draw_bullets(screen, camera_x, camera_y)

    # Player HUD (health bar)
    player.draw_hud(screen)

    # Game over overlay
    if not player.alive:
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        msg = font_big.render("YOU DIED", True, (220, 30, 30))
        screen.blit(msg, (settings.WIDTH // 2 - msg.get_width() // 2,
                           settings.HEIGHT // 2 - msg.get_height() // 2))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()