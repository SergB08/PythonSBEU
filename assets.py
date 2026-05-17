import pygame
import os

import settings

# ── Sound paths ───────────────────────────────────────────────────────────────
PlayerPistolShot = "sounds/stalkerPM.ogg"
TurretShot       = "sounds/stalkerMP5.ogg"

# ── Main game textures and icon ───────────────────────────────────────────────
def load_assets():

    icon = pygame.image.load(
        "textures/icon.png"
    ).convert()

    floor_tiles = []
    floor_path = "textures/floor"

    for file in os.listdir(floor_path):
        if file.endswith(".png"):
            img = pygame.image.load(
                os.path.join(floor_path, file)
            ).convert()
            img = pygame.transform.scale(img, (settings.TILE_SIZE, settings.TILE_SIZE))
            floor_tiles.append(img)

    wall_tiles = []
    wall_path = "textures/walls"

    for file in os.listdir(wall_path):
        if file.endswith(".png"):
            img = pygame.image.load(
                os.path.join(wall_path, file)
            ).convert()
            img = pygame.transform.scale(img, (settings.TILE_SIZE, settings.TILE_SIZE))
            wall_tiles.append(img)

    ladder = pygame.image.load("textures/drabina.png").convert()
    ladder = pygame.transform.scale(ladder, (settings.TILE_SIZE, settings.TILE_SIZE))

    return icon, floor_tiles, wall_tiles, ladder


def load_menu_textures():
    idle  = pygame.image.load("textures/ui/btn_idle.png").convert_alpha()
    hover = pygame.image.load("textures/ui/btn_hover.png").convert_alpha()
    click = pygame.image.load("textures/ui/btn_click.png").convert_alpha()
    return idle, hover, click


# ── Player sprites ────────────────────────────────────────────────────────────
def load_player_sprites2():
    tempidle  = pygame.image.load("textures/playerTemp/idleTemp.png").convert_alpha()
    tempwalk1 = pygame.image.load("textures/playerTemp/walk1Temp.png").convert_alpha()
    tempwalk2 = pygame.image.load("textures/playerTemp/walk2Temp.png").convert_alpha()
    
    
    
    
    head = pygame.image.load("textures/player/playerHead.png").convert_alpha()
    
    body = pygame.image.load("textures/player/body/playerBody.png").convert_alpha()
    bodyPistol = pygame.image.load("textures/player/body/playerBodyPistol.png").convert_alpha()
    
    legsIdle = pygame.image.load("textures/player/legs/playerLegsStatic.png").convert_alpha()
    legsStepL1 = pygame.image.load("textures/player/legs/playerLegsStepL1.png").convert_alpha()
    legsStepL2 = pygame.image.load("textures/player/legs/playerLegsStepL2.png").convert_alpha()
    legsStepR1 = pygame.image.load("textures/player/legs/playerLegsStepR1.png").convert_alpha()
    legsStepR2 = pygame.image.load("textures/player/legs/playerLegsStepR2.png").convert_alpha()
    
    playerLegsIdle = {"legsIdleAnim": legsIdle}
    playerLegsWalk = {"legsWalkAnim": [legsIdle, legsStepL1, legsStepL2, legsStepL1, legsIdle, legsStepR1, legsStepR2, legsStepR1]}
    
    playerIdle = {"tempIdleAnim": tempidle}
    playerWalk = {"tempWalk": [tempwalk1, tempwalk2]}
    return playerIdle, playerWalk, playerLegsIdle, playerLegsWalk, head, body, bodyPistol


# ── Turret sprites ────────────────────────────────────────────────────────────
def load_turret_sprites():
    def _load(filename):
        img = pygame.image.load(
            os.path.join("textures/turret", filename)
        ).convert_alpha()
        return pygame.transform.scale(img, (img.get_width() * 10, img.get_height() * 10))

    legs      = _load("legs.png")
    head_calm = _load("headcalm.png")
    head_ang1 = _load("headangry1.png")
    head_ang2 = _load("headangry2.png")

    return legs, head_calm, [head_ang1, head_ang2]