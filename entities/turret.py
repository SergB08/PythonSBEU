import random
import pygame
import math

import settings
import assets
from entities.muzzle_flash import MuzzleFlash

pygame.mixer.init()


# ─────────────────────────────────────────────────────────────────────────────
#  Floating damage number
# ─────────────────────────────────────────────────────────────────────────────

class DamageNumber:
    """A small number that floats upward and fades out after a hit."""

    FONT = None

    def __init__(self, screen_x, screen_y, amount, color=(255, 60, 60)):
        self.x      = float(screen_x)
        self.y      = float(screen_y)
        self.amount = amount
        self.color  = color
        self.alpha  = 255
        self.alive  = True
        self._vy    = -80

    def update(self, dt):
        self.y     += self._vy * dt
        self.alpha -= 320 * dt
        if self.alpha <= 0:
            self.alive = False

    def draw(self, screen):
        if DamageNumber.FONT is None:
            DamageNumber.FONT = pygame.font.SysFont(None, 30, bold=True)
        surf = DamageNumber.FONT.render(f"-{self.amount}", True, self.color)
        surf.set_alpha(max(0, int(self.alpha)))
        screen.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))


# ─────────────────────────────────────────────────────────────────────────────
#  Bullet direction helper
# ─────────────────────────────────────────────────────────────────────────────

def _angle_to_velocity(angle_deg, speed):
    rad = math.radians(angle_deg)
    return -math.sin(rad) * speed, -math.cos(rad) * speed


# ─────────────────────────────────────────────────────────────────────────────
#  Bullet drawing helper
# ─────────────────────────────────────────────────────────────────────────────

def _draw_bullet(surface, sx, sy, vx, vy, length, width, body_col, rim_col):
    spd = math.hypot(vx, vy)
    if spd < 1:
        pygame.draw.circle(surface, body_col, (sx, sy), width)
        return
    nx, ny = vx / spd, vy / spd
    px, py = -ny, nx

    hw = width / 2
    tail = (sx - nx * length * 0.35, sy - ny * length * 0.35)
    tip  = (sx + nx * length * 0.65, sy + ny * length * 0.65)

    c1 = (tail[0] + px * hw,       tail[1] + py * hw)
    c2 = (tail[0] - px * hw,       tail[1] - py * hw)
    c3 = (tip[0]  - px * hw * 0.2, tip[1]  - py * hw * 0.2)
    c4 = (tip[0]  + px * hw * 0.2, tip[1]  + py * hw * 0.2)

    pygame.draw.polygon(surface, body_col, [c1, c2, c3, c4])
    pygame.draw.line(surface, rim_col,
                     (int(c1[0]), int(c1[1])), (int(c4[0]), int(c4[1])), 1)


# ─────────────────────────────────────────────────────────────────────────────

class Bullet:
    """Turret bullet — brass look."""

    SPEED    = 7500
    DAMAGE   = 10
    LIFETIME = 3
    LENGTH   = 25
    WIDTH    = 6

    def __init__(self, x, y, angle_deg):
        self.x  = float(x)
        self.y  = float(y)
        self.vx, self.vy = _angle_to_velocity(angle_deg, self.SPEED)
        self.alive     = True
        self._lifetime = self.LIFETIME

    def update(self, dt, world):
        from level.world import WALL
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._lifetime -= dt
        if self._lifetime <= 0:
            self.alive = False
            return
        ts = settings.TILE_SIZE
        tx = int(self.x // ts)
        ty = int(self.y // ts)
        h, w = len(world.tiles), len(world.tiles[0])
        if 0 <= ty < h and 0 <= tx < w:
            if world.tiles[ty][tx] == WALL:
                self.alive = False
        else:
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        _draw_bullet(screen, sx, sy, self.vx, self.vy,
                     self.LENGTH, self.WIDTH,
                     (210, 140, 30), (255, 220, 100))


class PlayerBullet(Bullet):
    """Player bullet — steel look."""

    SPEED    = 2000
    DAMAGE   = 5
    LIFETIME = 1.5
    LENGTH   = 16
    WIDTH    = 4

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        _draw_bullet(screen, sx, sy, self.vx, self.vy,
                     self.LENGTH, self.WIDTH,
                     (170, 210, 235), (225, 245, 255))


# ─────────────────────────────────────────────────────────────────────────────

class Turret:
    """
    Stationary enemy turret.
    Layers: legs (static) + head (rotates toward player).
    States: idle → alert (calm head) → firing (angry head + shooting)
    """
    randomHPTurret = random.randrange(70, 120)

    MAX_HP         = randomHPTurret
    DETECT_RANGE   = 800
    FIRE_RANGE     = 750
    AIM_TIME       = 0.5
    FIRE_COOLDOWN  = 0.1 #### щоб зробити більшу скорострільність треба зробити коротше звук постріла
    HEAD_ROT_SPEED = 300
    TURRET_MUZZLE_BARREL_OFFSET = 70 

    ANGRY_ANIM_SPEED = 0.75
    SHOOT_SOUND      = None
    
    TURRET_SPRITE_OFFSET = 90  # adjust until sprites face correct direction

    #HEAD_SPRITE_OFFSET = 0

    def __init__(self, world_x, world_y, legs_img, head_idle, head_cautious, head_angry, initial_angle=0.0):
        self.world_x = float(world_x)
        self.world_y = float(world_y)

        self.hp    = self.MAX_HP
        self.alive = True
        
        self._idle_angle = initial_angle
        
        def prep(img):
            return pygame.transform.scale(img, (size, size))    

        size = 128  # adjust to taste

        self.legs_img      = prep(legs_img)
        self.head_idle     = prep(head_idle["headIdleAnim"])
        self.head_cautious = prep(head_cautious["headCautiousAnim"])
        self.head_angry    = [prep(f) for f in head_angry["headAngryAnim"]]

        self.head_angle   = 0.0
        self.state        = "idle"
        self._aim_timer   = 0.0
        self._fire_timer  = 0.0
        self._angry_frame = 0.0

        self.head_angle = initial_angle

        self.bullets        = []
        self.damage_numbers = []
        self.muzzle_flashes = []
        self._muzzle_frames = assets.load_muzzleFlash()

        if Turret.SHOOT_SOUND is None:
            Turret.SHOOT_SOUND = pygame.mixer.Sound(assets.TurretShot)

    # ── helpers ──────────────────────────────────────────────────────────── #

    def _angle_to_world_pos(self, tx, ty):
        dx =  tx - self.world_x
        dy = -(ty - self.world_y)
        return math.degrees(math.atan2(dy, dx)) - 90

    def _dist(self, px, py):
        return math.hypot(px - self.world_x, py - self.world_y)

    def _rotate_toward(self, target, dt):
        diff = (target - self.head_angle + 180) % 360 - 180
        step = self.HEAD_ROT_SPEED * dt
        if abs(diff) <= step:
            self.head_angle = target
            return True
        self.head_angle += math.copysign(step, diff)
        return False

    # ── update ───────────────────────────────────────────────────────────── #

    def update(self, dt, player, world):
        if not self.alive:
            return

        px, py = player.world_x, player.world_y
        dist   = self._dist(px, py)
        target = self._angle_to_world_pos(px, py)

        for b in self.bullets:
            b.update(dt, world)
        self.bullets = [b for b in self.bullets if b.alive]

        for mf in self.muzzle_flashes: mf.update(dt)
        self.muzzle_flashes = [mf for mf in self.muzzle_flashes if mf.alive]

        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

        if self.state == "idle":
            if dist <= self.DETECT_RANGE:
                self.state      = "alert"
                self._aim_timer = self.AIM_TIME
            self._rotate_toward(self._idle_angle, dt * 0.3)

        elif self.state == "alert":
            self._rotate_toward(target, dt)
            if dist > self.DETECT_RANGE * 1.2:
                self.state = "idle"
                return
            self._aim_timer -= dt
            if self._aim_timer <= 0:
                self.state       = "firing"
                self._fire_timer = 0.0

        elif self.state == "firing":
            aligned = self._rotate_toward(target, dt)
            if dist > self.DETECT_RANGE * 1.2:
                self.state = "idle"
                return
            self._fire_timer -= dt
            if self._fire_timer <= 0 and dist <= self.FIRE_RANGE and aligned:
                self._angry_frame += self.ANGRY_ANIM_SPEED * dt * 60
                self._shoot()
                self._fire_timer = self.FIRE_COOLDOWN

    def _shoot(self):
        self.bullets.append(Bullet(self.world_x, self.world_y, self.head_angle))
        self.muzzle_flashes.append(
            MuzzleFlash(self.head_angle, self._muzzle_frames, barrel_offset=self.TURRET_MUZZLE_BARREL_OFFSET, size=64)
        )
        Turret.SHOOT_SOUND.set_volume(settings.VOLUME)
        Turret.SHOOT_SOUND.play()
        self._fire_timer = self.FIRE_COOLDOWN

    def take_damage(self, amount, camera_x, camera_y):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y) - self.legs_img.get_height() // 2 - 20
        self.damage_numbers.append(DamageNumber(sx, sy, amount, (255, 80, 30)))
        if self.hp <= 0:
            self.alive = False

    # ── draw ─────────────────────────────────────────────────────────────── #

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return

        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        margin = 250
        if (sx < -margin or sx > settings.WIDTH  + margin or
                sy < -margin or sy > settings.HEIGHT + margin):
            return

        legs_rect = self.legs_img.get_rect(center=(sx, sy))
        screen.blit(self.legs_img, legs_rect.topleft)

        if self.state == "firing":
            fi  = int(self._angry_frame) % len(self.head_angry)
            src = self.head_angry[fi]
        elif self.state == "alert":
            src = self.head_cautious
        else:
            src = self.head_idle

        rotated = pygame.transform.rotate(src, self.head_angle + self.TURRET_SPRITE_OFFSET)
        hr      = rotated.get_rect(center=(sx, sy))
        screen.blit(rotated, hr.topleft)

        for mf in self.muzzle_flashes:
            mf.draw(screen, camera_x, camera_y, self.world_x, self.world_y)

        self._draw_health_bar(screen, sx, sy)

        for b in self.bullets:
            b.draw(screen, camera_x, camera_y)

        for dn in self.damage_numbers:
            dn.draw(screen)

    def _draw_health_bar(self, screen, sx, sy):
        bar_w = 120
        bar_h = 10
        bx    = sx - bar_w // 2
        by    = sy - self.legs_img.get_height() // 2 - 18
        ratio = max(0.0, self.hp / self.MAX_HP)

        pygame.draw.rect(screen, (10, 10, 10), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h))
        fill = (int(255 * (1 - ratio)), int(220 * ratio), 0)
        if ratio > 0:
            pygame.draw.rect(screen, fill, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1)

        if DamageNumber.FONT is None:
            DamageNumber.FONT = pygame.font.SysFont(None, 30, bold=True)
        font = pygame.font.SysFont(None, 18)
        txt  = font.render(f"{self.hp}/{self.MAX_HP}", True, (255, 255, 255))
        screen.blit(txt, (bx + bar_w // 2 - txt.get_width() // 2,
                           by + bar_h // 2 - txt.get_height() // 2))