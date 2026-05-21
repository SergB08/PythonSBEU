import pygame
import os
import settings

PlayerPistolShot = "sounds/gun/stalkerPM_shortened.ogg"      # звук пострілу гравця
TurretShot       = "sounds/gun/stalkerMP5_shortened.ogg"     # звук пострілу турелі
PlayerDeath      = "sounds/player/deathsound.wav"            # звук смерті гравця

# заздалегідь завантажений звук смерті для повторного використання
_death_sound = None

def get_death_sound():
    # завантажує звук смерті один раз та кешує його
    global _death_sound
    if _death_sound is None:
        try:
            _death_sound = pygame.mixer.Sound(PlayerDeath)
        except Exception:
            pass
    return _death_sound

#Основні текстури гри та іконка
def load_assets():
    # іконка вікна гри
    icon = pygame.image.load(
        "textures/slimeTemp.png"
    ).convert()

    # завантажує всі текстури підлоги з папки
    floor_tiles = []
    floor_path = "textures/floor"
    for file in os.listdir(floor_path):
        if file.endswith(".png"):
            img = pygame.image.load(
                os.path.join(floor_path, file)
            ).convert()
            img = pygame.transform.scale(img, (settings.TILE_SIZE, settings.TILE_SIZE))
            floor_tiles.append(img)

    # завантажує всі текстури стін з папки
    wall_tiles = []
    wall_path = "textures/walls"
    for file in os.listdir(wall_path):
        if file.endswith(".png"):
            img = pygame.image.load(
                os.path.join(wall_path, file)
            ).convert()
            img = pygame.transform.scale(img, (settings.TILE_SIZE, settings.TILE_SIZE))
            wall_tiles.append(img)

    # текстура виходу з рівня
    ladder = pygame.image.load("textures/exit.png").convert()
    ladder = pygame.transform.scale(ladder, (settings.TILE_SIZE, settings.TILE_SIZE))

    return icon, floor_tiles, wall_tiles, ladder


def load_menu_textures():
    # три стани кнопки
    idle  = pygame.image.load("textures/ui/btn_idle.png").convert_alpha()
    hover = pygame.image.load("textures/ui/btn_hover.png").convert_alpha()
    click = pygame.image.load("textures/ui/btn_click.png").convert_alpha()
    return idle, hover, click


#Спрайти гравця
def load_player_sprites2():
    # голова гравця
    playerHead = pygame.image.load("textures/player/playerHead.png").convert_alpha()
    
    # тіло гравця
    playerBody       = pygame.image.load("textures/player/body/playerBody.png").convert_alpha()
    playerBodyPistol = pygame.image.load("textures/player/body/playerBodyPistol.png").convert_alpha()
    
    # кадри анімації ніг
    playerLegsIdle   = pygame.image.load("textures/player/legs/playerLegsStatic.png").convert_alpha()
    playerLegsStepL1 = pygame.image.load("textures/player/legs/playerLegsStepL1.png").convert_alpha()
    playerLegsStepL2 = pygame.image.load("textures/player/legs/playerLegsStepL2.png").convert_alpha()
    playerLegsStepR1 = pygame.image.load("textures/player/legs/playerLegsStepR1.png").convert_alpha()
    playerLegsStepR2 = pygame.image.load("textures/player/legs/playerLegsStepR2.png").convert_alpha()
    
    # анімації ніг
    playerLegsIdleAnim = {"legsIdleAnim": playerLegsIdle}
    playerLegsWalkAnim = {"legsWalkAnim": [
        playerLegsIdle,
        playerLegsStepL1, playerLegsStepL2, playerLegsStepL1,
        playerLegsIdle,
        playerLegsStepR1, playerLegsStepR2, playerLegsStepR1
    ]}
    
    return playerLegsIdleAnim, playerLegsWalkAnim, playerHead, playerBody, playerBodyPistol


# ── Спрайти турелі ────────────────────────────────────────────────────────────
def load_turret_sprites():
    # голова турелі
    turretHead       = pygame.image.load("textures/turret/Head/headIdle.png").convert_alpha()
    turretHeadAngry1 = pygame.image.load("textures/turret/Head/headAngry1.png").convert_alpha()
    turretHeadAngry2 = pygame.image.load("textures/turret/Head/headAngry2.png").convert_alpha()

    # ноги турелі
    turretLegs = pygame.image.load("textures/turret/legsNew.png").convert_alpha()
    
    # словники анімацій голови турелі
    turretHeadIdleAnim     = {"headIdleAnim": turretHead}
    turretHeadCautiousAnim = {"headCautiousAnim": turretHeadAngry1}
    turretHeadAngryAnim    = {"headAngryAnim": [turretHeadAngry1, turretHeadAngry2]}
    
    return turretLegs, turretHeadIdleAnim, turretHeadAngryAnim, turretHeadCautiousAnim


def load_muzzleFlash():
    # три варіанти спалаху від пострілу
    muzzleFlash1 = pygame.image.load("textures/shot1.png").convert_alpha()
    muzzleFlash2 = pygame.image.load("textures/shot2.png").convert_alpha()
    muzzleFlash3 = pygame.image.load("textures/shot3.png").convert_alpha()
    return muzzleFlash1, muzzleFlash2, muzzleFlash3


def load_bullet_texture():
    # куля
    img = pygame.image.load("textures/bulletSmall.png").convert_alpha()
    return img


def load_item_sprites():
    # предмети
    medkit       = pygame.image.load("textures/items/medkit.png").convert_alpha()
    bandage      = pygame.image.load("textures/items/bandage.png").convert_alpha()
    ammoBoxSmall = pygame.image.load("textures/items/ammoBoxSmall.png").convert_alpha()
    ai2          = pygame.image.load("textures/items/ai2.png").convert_alpha()
    return medkit, bandage, ammoBoxSmall, ai2


def load_lootBox_texture():
    # текстура ящика з лутом
    box = pygame.image.load("textures/lootBox.png").convert_alpha()
    return box


def load_slime_frames():
    # тимчасова текстура слайма, три однакових кадри для анімації
    img = pygame.image.load("textures/slimeTemp.png").convert_alpha()
    return [img, img, img]