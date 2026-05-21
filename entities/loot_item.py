import pygame
import math
import random
import settings

PICKUP_RANGE = settings.TILE_SIZE * 1
ICON_SIZE = 48


class LootItem:

    # pickupable item lying on the floor.
    #drawn as an image. Picked up when player walks near and presses E.

    def __init__(self, world_x, world_y, item):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.item    = item          # inventory.Item instance
        self.alive   = True
        # Random rotation angle in degrees (0 to 360)
        self.rotation = random.uniform(0, 360)

    def near(self, px, py):
        return math.hypot(px - self.world_x, py - self.world_y) < PICKUP_RANGE

    def update(self, dt):
        pass

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        if sx < -ICON_SIZE or sx > settings.WIDTH + ICON_SIZE:
            return
        if sy < -ICON_SIZE or sy > settings.HEIGHT + ICON_SIZE:
            return

        # Icon with random rotation
        if self.item.image:
            img = pygame.transform.scale(self.item.image, (ICON_SIZE, ICON_SIZE))
            # Apply random rotation
            rotated_img = pygame.transform.rotate(img, self.rotation)
            # Get rect to center the rotated image
            rect = rotated_img.get_rect(center=(sx, sy))
            screen.blit(rotated_img, rect.topleft)
        else:
            # Fallback colored rectangle (also rotated)
            surf = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surf, self.item.color, surf.get_rect(), border_radius=6)
            pygame.draw.rect(surf, (200, 200, 200), surf.get_rect(), 1, border_radius=6)
            rotated_surf = pygame.transform.rotate(surf, self.rotation)
            rect = rotated_surf.get_rect(center=(sx, sy))
            screen.blit(rotated_surf, rect.topleft)