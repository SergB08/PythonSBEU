import pygame
class TickRate:
    def __init__(self, fps=60):                 # годинник pygame для відстеження часу між кадрами
        self.clock = pygame.time.Clock()
        self.fps = fps                          # цільова кількість кадрів на секунду
    def tick(self):
        dt = self.clock.tick(self.fps) / 1000   # обмежує fps та повертає дельта-час у секундах
        return dt
    def get_fps(self):
        return self.clock.get_fps()             # вертає поточну частоту кадрів