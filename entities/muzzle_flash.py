import pygame
import math
import random
import settings
 
 
class MuzzleFlash:
 
    DISPLAY_TIME = settings.SHOTEFFECT_SPEED# / 10
 
    def __init__(self, angle_deg, frames, barrel_offset=70, size=64):
 
        self.alive = True
        self._timer = self.DISPLAY_TIME
        self.angle = angle_deg
        self._barrel_offset = barrel_offset
 
        frame = random.choice(frames)
        self._surf = pygame.transform.scale(frame, (size, size))
 
    def update(self, dt):
        if not self.alive:
            return
        self._timer -= dt
        if self._timer <= 0:
            self.alive = False
 
    def draw(self, screen, camera_x, camera_y, world_x, world_y):
        if not self.alive:
            return
        rad = math.radians(self.angle)
        wx = world_x + (-math.sin(rad)) * self._barrel_offset
        wy = world_y + (-math.cos(rad)) * self._barrel_offset
        sx = int(wx - camera_x)
        sy = int(wy - camera_y)
        surf = pygame.transform.rotate(self._surf, self.angle + 90)
        screen.blit(surf, surf.get_rect(center=(sx, sy)).topleft)
 
    def draw_screen(self, screen, world_x, world_y):
        if not self.alive:
            return
        rad = math.radians(self.angle)
        cx = settings.WIDTH  // 2
        cy = settings.HEIGHT // 2
        sx = cx + (-math.sin(rad)) * self._barrel_offset
        sy = cy + (-math.cos(rad)) * self._barrel_offset
        surf = pygame.transform.rotate(self._surf, self.angle + 90)
        screen.blit(surf, surf.get_rect(center=(int(sx), int(sy))).topleft)