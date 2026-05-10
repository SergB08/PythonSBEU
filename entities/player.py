import pygame
import settings
from level.world import WALL


class Player:

    def __init__(self, animations, idles):

        self.world_x = 0
        self.world_y = 0

        self.width = 106
        self.height = 62

        self.animations = animations
        self.idle = idles

        self.direction = "down"
        self.anim_count = 0

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

        if keys[pygame.K_a]:
            new_x -= speed
            self.direction = "left"

        if keys[pygame.K_d]:
            new_x += speed
            self.direction = "right"

        if keys[pygame.K_w]:
            new_y -= speed
            self.direction = "up"

        if keys[pygame.K_s]:
            new_y += speed
            self.direction = "down"

        if not self.collides(world, new_x, self.world_y):
            self.world_x = new_x

        if not self.collides(world, self.world_x, new_y):
            self.world_y = new_y

        self.anim_count += settings.ANIMATION_SPEED * dt * 60

        if self.anim_count >= len(self.animations[self.direction]):
            self.anim_count = 0

    def draw(self, screen, keys):

        frame = int(self.anim_count)

        draw_x = settings.WIDTH // 2 - self.width // 2
        draw_y = settings.HEIGHT // 2 - self.height // 2

        if any(keys[k] for k in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]):
            img = self.animations[self.direction][frame]
        else:
            img = self.idle[self.direction]

        screen.blit(img, (draw_x, draw_y))