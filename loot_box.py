import pygame
import random
import settings

# ─────────────────────────────────────────────────────────────────────────────
#  LOOT BOX
#  Drawn as a brown crate (placeholder).
#  Destroyed by melee hits; drops ammo / medkits.
# ─────────────────────────────────────────────────────────────────────────────

BOX_SIZE   = 48
BOX_HP     = 3      # melee hits to break
BOX_COLOR  = (140, 90, 40)
BOX_BORDER = (80, 50, 20)

# TODO: load "textures/props/box.png" and "textures/props/box_broken.png"

class LootBox:
    def __init__(self, world_x, world_y):
        self.world_x  = float(world_x)
        self.world_y  = float(world_y)
        self.hp       = BOX_HP
        self.alive    = True
        self._shaking = 0.0   # visual hit feedback

        # pre-roll loot
        self.loot = self._roll_loot()

    def _roll_loot(self):
        from inventory import make_medkit, make_ammo_pistol
        drops = []
        if random.random() < 0.5:
            drops.append(make_medkit())
        ammo_count = random.randint(5, 20)
        if random.random() < 0.8:
            drops.append(make_ammo_pistol(ammo_count))
        return drops

    def hit(self, damage=1):
        """Called by melee attack. Returns list of items if broken."""
        self._shaking = 0.25
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return self.loot
        return []

    def update(self, dt):
        self._shaking = max(0, self._shaking - dt * 4)

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        # cull
        if sx < -BOX_SIZE or sx > settings.WIDTH + BOX_SIZE:
            return
        if sy < -BOX_SIZE or sy > settings.HEIGHT + BOX_SIZE:
            return

        # shake offset
        shake = 0
        if self._shaking > 0:
            import math
            shake = int(math.sin(self._shaking * 80) * 3)

        r = pygame.Rect(sx - BOX_SIZE // 2 + shake,
                        sy - BOX_SIZE // 2,
                        BOX_SIZE, BOX_SIZE)

        # placeholder crate drawing
        # TODO: replace with: screen.blit(box_sprite, r.topleft)
        pygame.draw.rect(screen, BOX_COLOR, r, border_radius=4)
        pygame.draw.rect(screen, BOX_BORDER, r, 2, border_radius=4)
        # cross mark
        pygame.draw.line(screen, BOX_BORDER,
                         (r.left + 4, r.top + 4), (r.right - 4, r.bottom - 4), 2)
        pygame.draw.line(screen, BOX_BORDER,
                         (r.right - 4, r.top + 4), (r.left + 4, r.bottom - 4), 2)

        # HP pips
        pip_r = 4
        gap   = 14
        total_w = BOX_HP * (pip_r * 2 + 2)
        px = sx - total_w // 2
        py = sy - BOX_SIZE // 2 - 12
        for i in range(BOX_HP):
            col = (80, 200, 80) if i < self.hp else (60, 60, 60)
            pygame.draw.circle(screen, col, (px + i * (pip_r * 2 + 2), py), pip_r)