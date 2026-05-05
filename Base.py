import pygame
import settings

from entities.player import Player

from assets import load_assets,load_map_textures , load_player_sprites

from levelGenerator import generate_level, build_tilemap, TILE_SIZE, WIDTH, HEIGHT, FLOOR_TEXTURE_PATH, WALL_TEXTURE_PATH

from tickrate import TickRate



pygame.init()

screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), flags=pygame.NOFRAME)
tickrate = TickRate(settings.FPS)

# Assets
bg = load_assets()
anim_player_idle, anim_player_walk = load_player_sprites()
floor_tiles = load_textures(FLOOR_TEXTURE_PATH, TILE_SIZE)
wall_tiles = load_textures(WALL_TEXTURE_PATH, TILE_SIZE)

# Level
grid, rooms = generate_level()
tilemap = build_tilemap(grid, floor_tiles, wall_tiles)

# Player
player = Player(anim_player_idle, anim_player_walk)

# Camera offset
cam_x = 0
cam_y = 0

running = True

while running:
    dt = tickrate.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                grid, rooms = generate_level()
                tilemap = build_tilemap(grid, floor_tiles, wall_tiles)

    keys = pygame.key.get_pressed()

    # Update player
    player.update(keys, dt)

    # Camera follows player
    cam_x = int(player.x - settings.WIDTH // 2)
    cam_y = int(player.y - settings.HEIGHT // 2)

    # Draw tilemap
    screen.fill((0, 0, 0))
    for ty in range(HEIGHT):
        for tx in range(WIDTH):
            tile = tilemap[ty][tx]
            if tile:
                screen.blit(tile, (tx * TILE_SIZE - cam_x, ty * TILE_SIZE - cam_y))

    # Draw player (always centered)
    player.draw(screen, keys)

    pygame.display.update()

pygame.quit()