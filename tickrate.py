import pygame
class TickRate:
    def __init__(self, fps=60):
        self.clock = pygame.time.Clock()
        self.fps = fps
    def tick(self):
        dt = self.clock.tick(self.fps) / 1000
        return dt
    def get_fps(self):
        return self.clock.get_fps()