import pygame
import math
import settings
from level.world import WALL


class Player:

    def __init__(self, idles, animations, rotation_speed=500):

        self.world_x = 0
        self.world_y = 0

        self.width = 106
        self.height = 62

        self.idle = idles
        self.animations = animations

        self.anim_count = 0
        self.angle = 0
        self.rotation_speed = rotation_speed

    def _get_angle_to_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_x = settings.WIDTH // 2
        screen_y = settings.HEIGHT // 2
        dx = mouse_x - screen_x
        dy = mouse_y - screen_y
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        return angle

    def collides(self, world, x, y):
        ts = settings.TILE_SIZE
        points = [
            (x - self.width/2, y - self.height/2),
            (x + self.width/2, y - self.height/2),
            (x - self.width/2, y + self.height/2),
            (x + self.width/2, y + self.height/2),
        ]
        for px, py in points:
            tx = int(px // ts)
            ty = int(py // ts)
            if world.tiles[ty][tx] == WALL:
                return True
        return False

    def update(self, keys, dt, world):
        speed = settings.PLAYER_SPEED * dt * 60
        new_x = self.world_x
        new_y = self.world_y
        moving = False

        if keys[pygame.K_a]:
            new_x -= speed
            moving = True
        if keys[pygame.K_d]:
            new_x += speed
            moving = True
        if keys[pygame.K_w]:
            new_y -= speed
            moving = True
        if keys[pygame.K_s]:
            new_y += speed
            moving = True

        if not self.collides(world, new_x, self.world_y):
            self.world_x = new_x
        if not self.collides(world, self.world_x, new_y):
            self.world_y = new_y

        if moving:
            self.anim_count += settings.ANIMATION_SPEED * dt * 60
            walk_frames = self.animations["tempWalk"]
            if self.anim_count >= len(walk_frames):
                self.anim_count = 0

        target_angle = self._get_angle_to_mouse()

        if self.rotation_speed == 0:
            self.angle = target_angle
        else:
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * min(1.0, self.rotation_speed * dt)

    def draw(self, screen, keys):
        moving = any(keys[k] for k in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s])

        if moving:
            frame = int(self.anim_count)
            img = self.animations["tempWalk"][frame]
        else:
            img = self.idle["tempIdleAnim"]

        rotated = pygame.transform.rotate(img, self.angle)
        rect = rotated.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
        screen.blit(rotated, rect.topleft)