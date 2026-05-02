import pygame
import settings
from controls import MOVE_KEYS, ROLL_KEY

class Player:
    def __init__(self, animations, idles):
        self.x = 300
        self.y = 350
        self.anim_count = 0
        self.animations = animations
        self.animations["right"]
        self.idle = idles
        self.idle["right"]
        
        self.direction = "down"
    def update(self, keys, dt):
        moving = False

        if keys[pygame.K_LEFT] and self.x > 300:
            self.x -= settings.PLAYER_SPEED * dt * 60
            self.direction = "left"
            moving = True

        elif keys[pygame.K_RIGHT] and self.x < 1600:
            self.x += settings.PLAYER_SPEED * dt * 60
            self.direction = "right"
            moving = True

        if keys[pygame.K_UP] and self.y > 120:
            self.y -= settings.PLAYER_SPEED * dt * 60
            self.direction = "up"
            moving = True

        elif keys[pygame.K_DOWN] and self.y < 900:
            self.y += settings.PLAYER_SPEED * dt * 60
            self.direction = "down"
            moving = True

        if moving:
            self.anim_count += settings.ANIMATION_SPEED * dt * 60
            if self.anim_count >= len(self.animations[self.direction]):
                self.anim_count = 0
        else:
            self.anim_count = 0

        return moving
    def draw(self, screen, keys):
        frame = int(self.anim_count)
        if any(keys[k] for k in MOVE_KEYS):
            screen.blit(self.animations[self.direction][frame], (self.x, self.y))
        else:
            screen.blit(self.idle[self.direction], (self.x, self.y))
                