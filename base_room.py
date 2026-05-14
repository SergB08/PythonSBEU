import pygame
import settings
import random

# ─────────────────────────────────────────────────────────────────────────────
#  BASE ROOM
#  Shown every 5 levels (and at level 0 = start).
#  Contains:
#    - Bed      (walk near + E  → sleep → heal all HP over time)
#    - Chest    (walk near + E  → open  → grants random loot)
#    - Portal   (walk near + E  → begin dungeon / next floor)
# ─────────────────────────────────────────────────────────────────────────────

BED_COLOR     = (180, 100, 100)
CHEST_COLOR   = (160, 120, 40)
PORTAL_COLOR1 = (80,  0,  200)
PORTAL_COLOR2 = (180, 80, 255)
FLOOR_COLOR   = (60,  55,  50)
WALL_COLOR    = (40,  38,  36)

INTERACT_RANGE = settings.TILE_SIZE * 2


class Prop:
    """Generic interactive prop drawn as a colored rectangle."""
    def __init__(self, world_x, world_y, w, h, color, label):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.w, self.h = w, h
        self.color   = color
        self.label   = label
        self._font   = None

    def near(self, px, py):
        import math
        return math.hypot(px - self.world_x, py - self.world_y) < INTERACT_RANGE

    def draw(self, screen, camera_x, camera_y):
        if self._font is None:
            self._font = pygame.font.SysFont(None, 22, bold=True)
        sx = int(self.world_x - camera_x) - self.w // 2
        sy = int(self.world_y - camera_y) - self.h // 2
        # TODO: replace with sprite blit when texture ready
        pygame.draw.rect(screen, self.color,
                         pygame.Rect(sx, sy, self.w, self.h), border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200),
                         pygame.Rect(sx, sy, self.w, self.h), 2, border_radius=6)
        lbl = self._font.render(self.label, True, (240, 240, 240))
        screen.blit(lbl, (sx + self.w // 2 - lbl.get_width()  // 2,
                           sy + self.h // 2 - lbl.get_height() // 2))


class Portal(Prop):
    """Animated portal — drawn as pulsing circles. Replace with sprite later."""
    def __init__(self, world_x, world_y):
        super().__init__(world_x, world_y, 80, 80, PORTAL_COLOR1, "PORTAL")
        self._anim = 0.0

    def update(self, dt):
        self._anim = (self._anim + dt * 2) % 1.0

    def draw(self, screen, camera_x, camera_y):
        import math
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)
        # outer glow rings
        for i in range(3):
            phase = (self._anim + i / 3) % 1.0
            r  = int(40 + phase * 20)
            a  = int(180 * (1 - phase))
            col = (int(80 + phase * 100), 0, int(200 + phase * 55))
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*col, a), (r + 2, r + 2), r, 3)
            screen.blit(surf, (sx - r - 2, sy - r - 2))
        # core
        # TODO: replace with: screen.blit(portal_sprite, ...)
        pygame.draw.circle(screen, PORTAL_COLOR2, (sx, sy), 22)
        pygame.draw.circle(screen, (255, 180, 255), (sx, sy), 10)
        if self._font is None:
            self._font = pygame.font.SysFont(None, 22, bold=True)
        lbl = self._font.render("PORTAL", True, (240, 200, 255))
        screen.blit(lbl, (sx - lbl.get_width() // 2, sy + 28))


class Bed(Prop):
    """Sleep to heal. Healing happens over time while player 'sleeps'."""
    HEAL_PER_SEC = 8
    SLEEP_TIME   = 4.0   # seconds to fully "sleep"

    def __init__(self, world_x, world_y):
        super().__init__(world_x, world_y, 100, 60, BED_COLOR, "BED")
        self.sleeping    = False
        self._sleep_timer= 0.0

    def start_sleep(self):
        self.sleeping     = True
        self._sleep_timer = self.SLEEP_TIME

    def update(self, dt, body_health):
        if self.sleeping:
            self._sleep_timer -= dt
            body_health.heal_all(int(self.HEAL_PER_SEC * dt))
            if self._sleep_timer <= 0:
                self.sleeping = False

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        if self.sleeping:
            sx = int(self.world_x - camera_x)
            sy = int(self.world_y - camera_y)
            if self._font is None:
                self._font = pygame.font.SysFont(None, 22, bold=True)
            zzz = self._font.render("Z Z Z", True, (200, 220, 255))
            screen.blit(zzz, (sx - zzz.get_width() // 2, sy - 60))


class Chest(Prop):
    """One-time loot chest."""
    def __init__(self, world_x, world_y):
        super().__init__(world_x, world_y, 70, 50, CHEST_COLOR, "CHEST")
        self.opened = False
        self._loot  = self._roll()

    def _roll(self):
        from inventory import make_medkit, make_ammo_pistol
        items = [make_medkit(), make_ammo_pistol(random.randint(10, 30))]
        return items

    def open(self):
        if self.opened:
            return []
        self.opened = True
        self.color  = (80, 60, 20)
        self.label  = "EMPTY"
        return self._loot

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)
        if not self.opened:
            # small lock icon placeholder
            pygame.draw.rect(screen, (200, 180, 50),
                             pygame.Rect(sx - 6, sy - 18, 12, 10), border_radius=2)
            pygame.draw.circle(screen, (200, 180, 50), (sx, sy - 22), 5, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  BASE ROOM SCENE
# ─────────────────────────────────────────────────────────────────────────────

ROOM_W = 1200
ROOM_H = 900

class BaseRoom:
    """
    Self-contained base-room scene.
    Call run(screen, dt, events, player) each frame.
    Returns "dungeon" when player uses the portal, else None.
    """
    def __init__(self):
        cx, cy = ROOM_W // 2, ROOM_H // 2
        ts = settings.TILE_SIZE

        self.portal = Portal(cx + 400, cy)
        self.bed    = Bed(cx - 320, cy + 80)
        self.chest  = Chest(cx, cy - 180)

        self._prompt_font = pygame.font.SysFont(None, 36, bold=True)
        self._title_font  = pygame.font.SysFont(None, 52, bold=True)

        # Floor surface (cached)
        self._bg = self._make_bg()

    def _make_bg(self):
        surf = pygame.Surface((ROOM_W, ROOM_H))
        surf.fill(FLOOR_COLOR)
        # Wall border
        border = 80
        for side in [
            pygame.Rect(0, 0, ROOM_W, border),
            pygame.Rect(0, ROOM_H - border, ROOM_W, border),
            pygame.Rect(0, 0, border, ROOM_H),
            pygame.Rect(ROOM_W - border, 0, border, ROOM_H),
        ]:
            pygame.draw.rect(surf, WALL_COLOR, side)
        # TODO: replace with tiled floor/wall textures
        return surf

    def run(self, screen, dt, events, player):
        """
        player : Player instance (for position + inventory + body_health)
        Returns "dungeon" or None.
        """
        import controls

        px, py = player.world_x, player.world_y
        # clamp camera so room stays centered
        camera_x = px - settings.WIDTH  // 2
        camera_y = py - settings.HEIGHT // 2

        # ── draw floor ──────────────────────────────────────────── #
        screen.blit(self._bg, (-camera_x % ROOM_W - ROOM_W, -camera_y % ROOM_H - ROOM_H))
        screen.blit(self._bg, (-camera_x, -camera_y))

        # ── update props ────────────────────────────────────────── #
        self.portal.update(dt)
        self.bed.update(dt, player.body_health)

        # ── draw props ──────────────────────────────────────────── #
        self.portal.draw(screen, camera_x, camera_y)
        self.bed.draw(screen, camera_x, camera_y)
        self.chest.draw(screen, camera_x, camera_y)

        # ── player draw ─────────────────────────────────────────── #
        keys = pygame.key.get_pressed()
        player.draw(screen, keys)
        player.body_health.draw_hud(screen)

        # ── interaction prompts & actions ───────────────────────── #
        prompt = None
        near_portal = self.portal.near(px, py)
        near_bed    = self.bed.near(px, py)
        near_chest  = self.chest.near(px, py)

        if near_portal:
            prompt = "[E] Enter Dungeon"
        elif near_bed and not self.bed.sleeping:
            prompt = "[E] Sleep (heal)"
        elif near_chest and not self.chest.opened:
            prompt = "[E] Open Chest"

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == controls.INTERACT_KEY:
                if near_portal:
                    return "dungeon"
                elif near_bed:
                    self.bed.start_sleep()
                elif near_chest:
                    loot = self.chest.open()
                    for item in loot:
                        player.inventory.add_item(item)

        if prompt:
            txt = self._prompt_font.render(prompt, True, (255, 230, 100))
            screen.blit(txt, (settings.WIDTH // 2 - txt.get_width() // 2,
                               settings.HEIGHT // 2 - 120))

        # sleeping overlay
        if self.bed.sleeping:
            fade = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 30, 120))
            screen.blit(fade, (0, 0))

        # room title
        title = self._title_font.render("BASE CAMP", True, (180, 180, 200))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 20))

        return None