import pygame
import random
import math
import settings

# ─────────────────────────────────────────────────────────────────────────────
#  LOOT BOX
#  Drawn as a crate texture.
#  Destroyed by melee hits or bullets; drops ammo / medkits.
# ─────────────────────────────────────────────────────────────────────────────

BOX_HP     = 3      # melee hits to break (bullets do more damage)
BOX_SIZE   = 128  # change this value to resize

class LootBox:
    def __init__(self, world_x, world_y):
        self.world_x  = float(world_x)
        self.world_y  = float(world_y)
        self.hp       = BOX_HP
        self.alive    = True
        self._shaking = 0.0   # visual hit feedback
        # Random rotation on spawn (0 to 360 degrees)
        self.rotation = random.uniform(0, 360)
        
        # Load texture
        from assets import load_lootBox_texture
        self._texture = load_lootBox_texture()
        # Cache rotated version
        self._cached_rotated = None
        self._cached_angle = None

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
        """Called by melee attack or bullets. Returns list of items if broken."""
        self._shaking = 0.25
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return self.loot
        return []

    def update(self, dt):
        self._shaking = max(0, self._shaking - dt * 4)

    def _get_rotated_texture(self):
        """Get cached rotated texture for current rotation."""
        if self._cached_rotated is None or self._cached_angle != self.rotation:
            scaled = pygame.transform.scale(self._texture, (BOX_SIZE, BOX_SIZE))
            self._cached_rotated = pygame.transform.rotate(scaled, self.rotation)
            self._cached_angle = self.rotation
        return self._cached_rotated

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
        shake_x = 0
        shake_y = 0
        if self._shaking > 0:
            shake_x = int(math.sin(self._shaking * 80) * 3)
            shake_y = int(math.cos(self._shaking * 80) * 2)

        # Get rotated texture
        rotated_texture = self._get_rotated_texture()
        rect = rotated_texture.get_rect(center=(sx + shake_x, sy + shake_y))
        screen.blit(rotated_texture, rect.topleft)