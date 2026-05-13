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


# Turret sprites
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