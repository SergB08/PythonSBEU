import pygame
import os

import settings

# ── Sound paths ───────────────────────────────────────────────────────────────
PlayerPistolShot = "sounds/gun/stalkerPM_shortened.ogg"
TurretShot       = "sounds/gun/stalkerMP5_shortened.ogg"

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
    playerHead = pygame.image.load("textures/player/playerHead.png").convert_alpha()
    
    playerBody = pygame.image.load("textures/player/body/playerBody.png").convert_alpha()
    playerBodyPistol = pygame.image.load("textures/player/body/playerBodyPistol.png").convert_alpha()
    
    playerLegsIdle = pygame.image.load("textures/player/legs/playerLegsStatic.png").convert_alpha()
    playerLegsStepL1 = pygame.image.load("textures/player/legs/playerLegsStepL1.png").convert_alpha()
    playerLegsStepL2 = pygame.image.load("textures/player/legs/playerLegsStepL2.png").convert_alpha()
    playerLegsStepR1 = pygame.image.load("textures/player/legs/playerLegsStepR1.png").convert_alpha()
    playerLegsStepR2 = pygame.image.load("textures/player/legs/playerLegsStepR2.png").convert_alpha()
    
    playerLegsIdleAnim = {"legsIdleAnim": playerLegsIdle}
    playerLegsWalkAnim = {"legsWalkAnim": [playerLegsIdle, playerLegsStepL1, playerLegsStepL2, playerLegsStepL1, playerLegsIdle, playerLegsStepR1, playerLegsStepR2, playerLegsStepR1]}
    
    return playerLegsIdleAnim, playerLegsWalkAnim, playerHead, playerBody, playerBodyPistol

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