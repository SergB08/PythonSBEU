import pygame
import math
import settings
from controls import MOVE_KEYS

class Player:
    def __init__(self, idle_anim, walk_anim):
        self.x = 300
        self.y = 350

        # Animation
        self.anim_count = 0
        self.idle = idle_anim["idle"]
        self.walk = walk_anim["walk"]

        # Rotation
        self.angle = 0
        self.rotation_smoothness = 0  # 0 = instant, try 0.1 for smooth

    def update(self, keys, dt):
        moving = False

        if keys[pygame.K_LEFT]:
            self.x -= settings.PLAYER_SPEED * dt * 60
            moving = True

        if keys[pygame.K_RIGHT]:
            self.x += settings.PLAYER_SPEED * dt * 60
            moving = True

        if keys[pygame.K_UP]:
            self.y -= settings.PLAYER_SPEED * dt * 60
            moving = True

        if keys[pygame.K_DOWN]:
            self.y += settings.PLAYER_SPEED * dt * 60
            moving = True

        # Animation
        if moving:
            self.anim_count += settings.ANIMATION_SPEED * dt * 60
            if self.anim_count >= len(self.walk):
                self.anim_count = 0
        else:
            self.anim_count = 0

        # 🔄 Rotate toward mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - self.x
        dy = mouse_y - self.y

        target_angle = math.degrees(math.atan2(-dy, dx)) - 90 ###(-90 якщо спрайт дивиться наліво)

        if self.rotation_smoothness == 0:
            self.angle = target_angle
        else:
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * self.rotation_smoothness

        return moving

    def draw(self, screen, keys):
        # Choose sprite
        if any(keys[k] for k in MOVE_KEYS):
            frame = int(self.anim_count)
            image = self.walk[frame]
        else:
            image = self.idle

        # Rotate
        rotated = pygame.transform.rotate(image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))

        screen.blit(rotated, rect.topleft)