import pygame
import math
import settings
import assets
from entities.turret import PlayerBullet, _angle_to_velocity

# ─────────────────────────────────────────────────────────────────────────────
#  PISTOL
#  - RMB to aim (ADS), LMB fires ONLY while aiming
#  - Has its own ammo count; draws from player inventory when reloading
# ─────────────────────────────────────────────────────────────────────────────

class Pistol:
    SHOOT_COOLDOWN  = 0.25
    MAG_SIZE        = 12
    RELOAD_TIME     = 1.6
    ADS_FOV_FACTOR  = 0.6      # unused for now; hook for zoom later
    SOUND           = None

    def __init__(self):
        self.ammo_in_mag  = self.MAG_SIZE
        self.aiming       = False          # True while RMB held
        self._shoot_timer = self.SHOOT_COOLDOWN * 3
        self._reload_timer= 0.0
        self.reloading    = False
        self.bullets      = []             # list of PlayerBullet
        self._pending_ammo = 0

        # TODO: load pistol sprite
        # self.sprite_idle = pygame.image.load("textures/weapons/pistol_idle.png").convert_alpha()
        # self.sprite_ads  = pygame.image.load("textures/weapons/pistol_ads.png").convert_alpha()

        if Pistol.SOUND is None:
            try:
                Pistol.SOUND = pygame.mixer.Sound(assets.PlayerPistolShot)
            except Exception:
                pass

    def update(self, dt, mouse_buttons, keys, player_angle, player_x, player_y,
               world, inventory=None):
        """
        mouse_buttons : pygame.mouse.get_pressed()
        inventory     : Inventory instance (to pull ammo from)
        """
        self.aiming = bool(mouse_buttons[2])   # RMB

        # reload key R
        if keys[pygame.K_r] and not self.reloading and self.ammo_in_mag < self.MAG_SIZE:
            self._start_reload(inventory)

        if self.reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self.reloading = False
                self.finish_reload()

        self._shoot_timer -= dt

        # Shoot: LMB + aiming + not reloading + ammo
        if (mouse_buttons[0] and self.aiming
                and not self.reloading
                and self._shoot_timer <= 0
                and self.ammo_in_mag > 0):
            self._fire(player_angle, player_x, player_y)

        # update bullets
        for b in self.bullets:
            b.update(dt, world)
        self.bullets = [b for b in self.bullets if b.alive]

    def _fire(self, angle, x, y):
        self.bullets.append(PlayerBullet(x, y, angle))
        self.ammo_in_mag -= 1
        self._shoot_timer = self.SHOOT_COOLDOWN
        if Pistol.SOUND:
            Pistol.SOUND.set_volume(settings.VOLUME)
            Pistol.SOUND.play()

    def _start_reload(self, inventory):
        needed = self.MAG_SIZE - self.ammo_in_mag
        if inventory:
            got = inventory.remove_item("ammo_pistol", needed)
        else:
            got = needed
        if got > 0:
            self.reloading     = True
            self._reload_timer = self.RELOAD_TIME
            self._pending_ammo = got

    def finish_reload(self):
        self.ammo_in_mag = min(self.MAG_SIZE,
                                self.ammo_in_mag + self._pending_ammo)
        self._pending_ammo = 0

    def draw_bullets(self, screen, camera_x, camera_y):
        for b in self.bullets:
            b.draw(screen, camera_x, camera_y)

    def draw_hud(self, screen):
        """Small ammo counter bottom-right."""
        font = pygame.font.SysFont(None, 32, bold=True)
        if self.reloading:
            txt = font.render("RELOADING...", True, (255, 200, 50))
        else:
            txt = font.render(f"{self.ammo_in_mag} / {self.MAG_SIZE}", True, (230, 230, 230))
        screen.blit(txt, (settings.WIDTH - txt.get_width() - 20,
                           settings.HEIGHT - 60))

        if self.aiming:
            # ADS crosshair
            cx, cy = settings.WIDTH // 2, settings.HEIGHT // 2
            col = (255, 50, 50)
            pygame.draw.line(screen, col, (cx - 20, cy), (cx + 20, cy), 2)
            pygame.draw.line(screen, col, (cx, cy - 20), (cx, cy + 20), 2)
            pygame.draw.circle(screen, col, (cx, cy), 14, 1)
        else:
            # Hip-fire loose crosshair
            cx, cy = settings.WIDTH // 2, settings.HEIGHT // 2
            col = (200, 200, 200)
            gap = 18
            pygame.draw.line(screen, col, (cx - 30, cy), (cx - gap, cy), 2)
            pygame.draw.line(screen, col, (cx + gap, cy), (cx + 30, cy), 2)
            pygame.draw.line(screen, col, (cx, cy - 30), (cx, cy - gap), 2)
            pygame.draw.line(screen, col, (cx, cy + gap), (cx, cy + 30), 2)


# ─────────────────────────────────────────────────────────────────────────────
#  FIST (empty-hand melee)
# ─────────────────────────────────────────────────────────────────────────────

PUNCH_RANGE   = 80      # pixels
PUNCH_DAMAGE  = 15
PUNCH_COOLDOWN= 0.5

class Fist:
    """Used when hotbar slot is empty or no weapon equipped."""
    def __init__(self):
        self._timer  = 0.0
        self.punching = False
        self._punch_flash = 0.0

    def update(self, dt, mouse_buttons, player_x, player_y,
               player_angle, turrets):
        self._timer -= dt
        self._punch_flash = max(0, self._punch_flash - dt * 3)
        # LMB punch — no aiming required
        if mouse_buttons[0] and self._timer <= 0:
            self._timer = PUNCH_COOLDOWN
            self.punching = True
            self._punch_flash = 0.4
            self._do_punch(player_x, player_y, player_angle, turrets)
        else:
            self.punching = False

    def _do_punch(self, px, py, angle, turrets):
        import math
        rad = math.radians(angle)
        tx  = px - math.sin(rad) * PUNCH_RANGE
        ty  = py - math.cos(rad) * PUNCH_RANGE
        for turret in turrets:
            if not turret.alive:
                continue
            dx = turret.world_x - tx
            dy = turret.world_y - ty
            if math.hypot(dx, dy) < 80:
                turret.take_damage(PUNCH_DAMAGE, 0, 0)

    def draw_hud(self, screen):
        cx, cy = settings.WIDTH // 2, settings.HEIGHT // 2
        col = (255, int(200 * (1 - self._punch_flash)), 50) if self._punch_flash > 0 \
              else (180, 180, 180)
        # simple fist crosshair: small circle
        pygame.draw.circle(screen, col, (cx, cy), 10, 2)
        pygame.draw.line(screen, col, (cx - 16, cy), (cx + 16, cy), 2)
        pygame.draw.line(screen, col, (cx, cy - 16), (cx, cy + 16), 2)