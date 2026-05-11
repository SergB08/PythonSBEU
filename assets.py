import pygame
import os

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


def load_player_sprites():

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
    }

    idles = {
        "up": stayup,
        "down": staydown,
        "left": stayl,
        "right": stayr
    }

    return animations, idles