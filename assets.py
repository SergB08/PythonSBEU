import pygame
def load_assets():
    icon = pygame.image.load("images/icon.png").convert_alpha()
    bg = pygame.image.load("floors/floor mainwood.jpg").convert()
    
    return icon, bg
def load_player_sprites():

    up1 = pygame.image.load("images_walk/up1.png").convert_alpha()
    up2 = pygame.image.load("images_walk/up2.png").convert_alpha()

    down1 = pygame.image.load("images_walk/down1.png").convert_alpha()
    down2 = pygame.image.load("images_walk/down2.png").convert_alpha()

    l1 = pygame.image.load("images_walk/l1.png").convert_alpha()
    l2 = pygame.image.load("images_walk/l2.png").convert_alpha()

    r1 = pygame.image.load("images_walk/r1.png").convert_alpha()
    r2 = pygame.image.load("images_walk/r2.png").convert_alpha()

    stayup = pygame.image.load("images_walk/stayup.png").convert_alpha()
    staydown = pygame.image.load("images_walk/staydown.png").convert_alpha()
    stayl = pygame.image.load("images_walk/stayl.png").convert_alpha()
    stayr = pygame.image.load("images_walk/stayr.png").convert_alpha()

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