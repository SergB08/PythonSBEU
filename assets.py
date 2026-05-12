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


### UDALIT vvv
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
###UDALIT ^^^


# Player sprites
def load_player_sprites2():
    tempidle = pygame.image.load(
        "textures/playerTemp/idleTemp.png"
    ).convert_alpha()
    tempwalk1 = pygame.image.load(
        "textures/playerTemp/walk1Temp.png"
    ).convert_alpha()
    tempwalk2 = pygame.image.load(
        "textures/playerTemp/walk2Temp.png"
    ).convert_alpha()

    playerIdle = {
        "tempIdleAnim": tempidle
    }
    playerWalk = {
        "tempWalk": [tempwalk1, tempwalk2]
    }
    return playerIdle, playerWalk



def load_turret_sprites():
    """
    Returns (legs_img, head_calm_img, [head_angry1_img, head_angry2_img])
    All images are scaled to TURRET_SIZE × TURRET_SIZE.
    """
    def _load(filename):
        img = pygame.image.load(
            os.path.join("textures/turret", filename)
        ).convert_alpha()
        return pygame.transform.scale(img, (img.get_width()*10, img.get_height()*10))

    legs       = _load("legs.png")
    head_calm  = _load("headcalm.png")
    head_ang1  = _load("headangry1.png")
    head_ang2  = _load("headangry2.png")

    return legs, head_calm, [head_ang1, head_ang2]