import pygame
import os


### OLD BG TEXTURE
### DELETE NAHUY
def load_assets(): 
    bg = pygame.image.load("floors/floor mainwood.jpg").convert()
    
    return bg


### MAP TEXTURES
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
def load_player_sprites():
    player_idle = pygame.image.load("textures/temp_player/idle.png").convert_alpha()
    player_walk1 = pygame.image.load("textures/temp_player/walk1.png").convert_alpha()
    player_walk2 = pygame.image.load("textures/temp_player/walk2.png").convert_alpha()

    anim_player_walk = 
    {
        "walk": [player_walk1, player_walk2]
    }
    anim_player_idle = 
    {
        "idle": player_idle
    }

    return anim_player_idle, anim_player_walk