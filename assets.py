import pygame
import os

<<<<<<< HEAD
import settings


def load_assets():

    icon = pygame.image.load(
        "images/icon.png"
    ).convert()
    floor_tiles = []

    floor_path = "textures/floor"

    for file in os.listdir(floor_path):

        if file.endswith(".png"):

            img = pygame.image.load(
                os.path.join(
                    floor_path,
                    file
                )
            ).convert()

            img = pygame.transform.scale(
                img,
                (
                    settings.TILE_SIZE,
                    settings.TILE_SIZE
                )
            )

            floor_tiles.append(img)
    wall_tiles = []

    wall_path = "textures/walls"

    for file in os.listdir(wall_path):

        if file.endswith(".png"):

            img = pygame.image.load(
                os.path.join(
                    wall_path,
                    file
                )
            ).convert()

            img = pygame.transform.scale(
                img,
                (
                    settings.TILE_SIZE,
                    settings.TILE_SIZE
                )
            )

            wall_tiles.append(img)

    return icon, floor_tiles, wall_tiles


=======

### OLD BG TEXTURE
### DELETE NAHUY
def load_assets(): 
    bg = pygame.image.load("floors/floor mainwood.jpg").convert()
    
    return bg


### MAP TEXTURES
FLOOR_TEXTURE_PATH = "textures/floor"
WALL_TEXTURE_PATH = "textures/walls"
def _load_texture_folder(folder, tile_size):
    textures = []
    if not os.path.exists(folder):
        print(f"Missing folder: {folder}")
        return textures

    for file in sorted(os.listdir(folder)):
        path = os.path.join(folder, file)
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (tile_size, tile_size))
            textures.append(img)
        except:
            pass

    return textures

def load_map_textures(floor_path, wall_path, tile_size):
    floor_tiles, wall_tiles = load_map_textures(FLOOR_TEXTURE_PATH, WALL_TEXTURE_PATH, TILE_SIZE)
    
    return floor_tiles, wall_tiles


### PLAYER SPRITES/ANIMATIONS
>>>>>>> main
def load_player_sprites():
    player_idle = pygame.image.load("textures/temp_player/idle.png").convert_alpha()
    player_walk1 = pygame.image.load("textures/temp_player/walk1.png").convert_alpha()
    player_walk2 = pygame.image.load("textures/temp_player/walk2.png").convert_alpha()

<<<<<<< HEAD
    up1 = pygame.image.load(
        "images_walk/up1.png"
    ).convert_alpha()

    up2 = pygame.image.load(
        "images_walk/up2.png"
    ).convert_alpha()

    down1 = pygame.image.load(
        "images_walk/down1.png"
    ).convert_alpha()

    down2 = pygame.image.load(
        "images_walk/down2.png"
    ).convert_alpha()

    l1 = pygame.image.load(
        "images_walk/l1.png"
    ).convert_alpha()

    l2 = pygame.image.load(
        "images_walk/l2.png"
    ).convert_alpha()

    r1 = pygame.image.load(
        "images_walk/r1.png"
    ).convert_alpha()

    r2 = pygame.image.load(
        "images_walk/r2.png"
    ).convert_alpha()

    stayup = pygame.image.load(
        "images_walk/stayup.png"
    ).convert_alpha()

    staydown = pygame.image.load(
        "images_walk/staydown.png"
    ).convert_alpha()

    stayl = pygame.image.load(
        "images_walk/stayl.png"
    ).convert_alpha()

    stayr = pygame.image.load(
        "images_walk/stayr.png"
    ).convert_alpha()

    animations = {
        "up": [up1, up2],
        "down": [down1, down2],
        "left": [l1, l2],
        "right": [r1, r2]
=======
    anim_player_walk = {
        "walk": [player_walk1, player_walk2]
    }
    anim_player_idle = {
        "idle": player_idle
>>>>>>> main
    }

    return anim_player_idle, anim_player_walk