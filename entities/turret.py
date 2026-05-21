import random
import pygame
import math

import settings
import assets
from entities.muzzle_flash import MuzzleFlash
from assets import load_bullet_texture

_BULLET_TEX = None  # cached bullet texture, loaded once on first use

pygame.mixer.init()

class DamageNumber:
    #A number that floats upward and fades out after a hit.
    FONT = None  # shared font, initialized on first draw

    def __init__(self, screen_x, screen_y, amount, color=(255, 60, 60)):
        self.x      = float(screen_x)
        self.y      = float(screen_y)
        self.amount = amount
        self.color  = color
        self.alpha  = 255       # starts fully opaque
        self.alive  = True
        self._vy    = -80       # upward drift speed in pixels/sec

    def update(self, dt):
        self.y     += self._vy * dt
        self.alpha -= 320 * dt  # fade out over ~0.8 seconds
        if self.alpha <= 0:
            self.alive = False

    def draw(self, screen):
        if DamageNumber.FONT is None:
            DamageNumber.FONT = pygame.font.SysFont(None, 30, bold=True)
        surf = DamageNumber.FONT.render(f"-{self.amount}", True, self.color)
        surf.set_alpha(max(0, int(self.alpha)))
        screen.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))


def _angle_to_velocity(angle_deg, speed):
    #Converts an angle in degrees to an (vx, vy) velocity tuple at the given speed
    rad = math.radians(angle_deg)
    return -math.sin(rad) * speed, -math.cos(rad) * speed


def _get_bullet_tex():
    #returns the bullet texture, loading it once and caching it
    global _BULLET_TEX
    if _BULLET_TEX is None:
        _BULLET_TEX = load_bullet_texture()
    return _BULLET_TEX


def _has_line_of_sight(world, x1, y1, x2, y2):
    #returns True if there are no wall tiles between two world-space points.
    #uses Bresenham's line algorithm on the tile grid

    from level.world import WALL
    ts = settings.TILE_SIZE
    tx1, ty1 = int(x1 // ts), int(y1 // ts)
    tx2, ty2 = int(x2 // ts), int(y2 // ts)

    dx = abs(tx2 - tx1)
    dy = abs(ty2 - ty1)
    sx = 1 if tx1 < tx2 else -1
    sy = 1 if ty1 < ty2 else -1
    err = dx - dy

    x, y = tx1, ty1
    h = len(world.tiles)
    w = len(world.tiles[0])

    while True:
        if 0 <= y < h and 0 <= x < w:
            if world.tiles[y][x] == WALL:
                return False
        else:
            return False
        if x == tx2 and y == ty2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x   += sx
        if e2 < dx:
            err += dx
            y   += sy

    return True


#  Both turret and player bullets live here for now.

class Bullet:
    #turret bullet - lower damage and longer lifetime than player bullet
    SPEED    = 5000   # pixels per second
    DAMAGE   = 10
    LIFETIME = 3      # seconds before auto-despawn
    LENGTH   = 32     # sprite dimensions
    WIDTH    = 32

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
        # kill bullet if it enters a wall tile or goes out of bounds
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
        tex     = _get_bullet_tex()
        scaled  = pygame.transform.scale(tex, (self.LENGTH, self.WIDTH))
        angle   = math.degrees(math.atan2(-self.vy, self.vx))
        rotated = pygame.transform.rotate(scaled, angle)
        screen.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)


class PlayerBullet(Bullet):
    #Player bullet - higher damage and shorter lifetime than turret bullet
    SPEED    = 5000
    DAMAGE   = 25
    LIFETIME = 1.5
    LENGTH   = 32
    WIDTH    = 32

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        tex     = _get_bullet_tex()
        scaled  = pygame.transform.scale(tex, (self.LENGTH, self.WIDTH))
        angle   = math.degrees(math.atan2(-self.vy, self.vx))
        rotated = pygame.transform.rotate(scaled, angle)
        screen.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)



class Turret:
    randomHPTurret = random.randrange(70, 120)  # random max HP per instance

    MAX_HP         = randomHPTurret
    DETECT_RANGE   = 800   # pixels — player spotted within this range
    FIRE_RANGE     = 750   # pixels — turret shoots within this range
    AIM_TIME       = 0.5   # seconds to transition from alert to firing
    FIRE_COOLDOWN  = 0.1   # seconds between shots
    HEAD_ROT_SPEED = 300   # degrees per second
    TURRET_MUZZLE_BARREL_OFFSET = 70  # pixel offset for muzzle flash position

    ANGRY_ANIM_SPEED = 0.75   # angry head animation framerate multiplier
    SHOOT_SOUND      = None   # shared sound, loaded once

    TURRET_SPRITE_OFFSET = 90  # rotation correction for sprite alignment

    def __init__(self, world_x, world_y, legs_img, head_idle, head_cautious, head_angry, initial_angle=0.0):
        self.world_x = float(world_x)
        self.world_y = float(world_y)

        self.hp    = self.MAX_HP
        self.alive = True

        self._idle_angle = initial_angle  # angle the turret faces when idle

        def prep(img):
            return pygame.transform.scale(img, (size, size))

        size = 128  # turret sprite render size

        self.legs_img      = prep(legs_img)
        self.head_idle     = prep(head_idle["headIdleAnim"])
        self.head_cautious = prep(head_cautious["headCautiousAnim"])
        self.head_angry    = [prep(f) for f in head_angry["headAngryAnim"]]

        self.head_angle   = initial_angle  # current head rotation in degrees
        self.state        = "idle"         # current AI state
        self._aim_timer   = 0.0            # counts down before switching to firing
        self._fire_timer  = 0.0            # counts down between shots
        self._angry_frame = 0.0            # animation frame counter for firing state

        self.bullets        = []
        self.damage_numbers = []
        self.muzzle_flashes = []
        self._muzzle_frames = assets.load_muzzleFlash()

        # load shoot sound once shared across all turrets
        if Turret.SHOOT_SOUND is None:
            Turret.SHOOT_SOUND = pygame.mixer.Sound(assets.TurretShot)


    def _angle_to_world_pos(self, tx, ty):
        #returns the angle in degrees from this turret toward a world position
        dx =  tx - self.world_x
        dy = -(ty - self.world_y)
        return math.degrees(math.atan2(dy, dx)) - 90

    def _dist(self, px, py):
        #returns pixel distance from this turret to a point
        return math.hypot(px - self.world_x, py - self.world_y)

    def _rotate_toward(self, target, dt):
        """
        Rotates head_angle toward target by HEAD_ROT_SPEED * dt.
        Returns True when fully aligned.
        """
        diff = (target - self.head_angle + 180) % 360 - 180
        step = self.HEAD_ROT_SPEED * dt
        if abs(diff) <= step:
            self.head_angle = target
            return True
        self.head_angle += math.copysign(step, diff)
        return False



    def update(self, dt, player, world):
        if not self.alive:
            return

        px, py = player.world_x, player.world_y
        dist   = self._dist(px, py)
        target = self._angle_to_world_pos(px, py)

        # update active bullets, muzzle flashes, and damage numbers
        for b in self.bullets:
            b.update(dt, world)
        self.bullets = [b for b in self.bullets if b.alive]

        for mf in self.muzzle_flashes:
            mf.update(dt)
        self.muzzle_flashes = [mf for mf in self.muzzle_flashes if mf.alive]

        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

        # line-of-sight check — done once per frame
        los = _has_line_of_sight(world, self.world_x, self.world_y, px, py)

        if self.state == "idle":
            # slowly sweep at idle angle; switch to alert if player spotted
            if dist <= self.DETECT_RANGE and los:
                self.state      = "alert"
                self._aim_timer = self.AIM_TIME
            self._rotate_toward(self._idle_angle, dt * 0.3)

        elif self.state == "alert":
            # track player; if player leaves range/LOS go back to idle
            self._rotate_toward(target, dt)
            if dist > self.DETECT_RANGE * 1.2 or not los:
                self.state = "idle"
                return
            self._aim_timer -= dt
            if self._aim_timer <= 0:
                self.state       = "firing"
                self._fire_timer = 0.0

        elif self.state == "firing":
            # shoot when aligned; retreat to idle if player escapes
            aligned = self._rotate_toward(target, dt)
            if dist > self.DETECT_RANGE * 1.2 or not los:
                self.state = "idle"
                return
            self._fire_timer -= dt
            if self._fire_timer <= 0 and dist <= self.FIRE_RANGE and aligned:
                self._angry_frame += self.ANGRY_ANIM_SPEED * dt * 60
                self._shoot()
                self._fire_timer = self.FIRE_COOLDOWN

    def _shoot(self):
        #spawns a bullet at the barrel tip and plays the shoot sound
        rad = math.radians(self.head_angle)
        offset_x = -math.sin(rad) * 70
        offset_y = -math.cos(rad) * 70
        self.bullets.append(
            Bullet(self.world_x + offset_x, self.world_y + offset_y, self.head_angle)
        )
        self.muzzle_flashes.append(
            MuzzleFlash(self.head_angle, self._muzzle_frames,
                        barrel_offset=self.TURRET_MUZZLE_BARREL_OFFSET, size=64)
        )
        Turret.SHOOT_SOUND.set_volume(settings.VOLUME)
        Turret.SHOOT_SOUND.play()
        self._fire_timer = self.FIRE_COOLDOWN

    def take_damage(self, amount, camera_x, camera_y):
        #Reduces HP and spawns a floating damage number. Kills turret at 0 HP.
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y) - self.legs_img.get_height() // 2 - 20
        self.damage_numbers.append(DamageNumber(sx, sy, amount, (255, 80, 30)))
        if self.hp <= 0:
            self.alive = False



    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return

        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        # cull if off-screen
        margin = 250
        if (sx < -margin or sx > settings.WIDTH  + margin or
                sy < -margin or sy > settings.HEIGHT + margin):
            return

        # draw legs (static rotation)
        rotated_legs = pygame.transform.rotate(
            self.legs_img, self._idle_angle + self.TURRET_SPRITE_OFFSET)
        screen.blit(rotated_legs, rotated_legs.get_rect(center=(sx, sy)).topleft)

        # pick head sprite based on current state
        if self.state == "firing":
            fi  = int(self._angry_frame) % len(self.head_angry)
            src = self.head_angry[fi]
        elif self.state == "alert":
            src = self.head_cautious
        else:
            src = self.head_idle

        # draw head rotated toward player
        rotated = pygame.transform.rotate(src, self.head_angle + self.TURRET_SPRITE_OFFSET)
        screen.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)

        for mf in self.muzzle_flashes:
            mf.draw(screen, camera_x, camera_y, self.world_x, self.world_y)

        self._draw_health_bar(screen, sx, sy)

        for b in self.bullets:
            b.draw(screen, camera_x, camera_y)

        for dn in self.damage_numbers:
            dn.draw(screen)

    def _draw_health_bar(self, screen, sx, sy):
        #Draws a colour-coded HP bar with numeric readout above the turret
        bar_w = 120
        bar_h = 10
        bx    = sx - bar_w // 2
        by    = sy - self.legs_img.get_height() // 2 - 18
        ratio = max(0.0, self.hp / self.MAX_HP)

        pygame.draw.rect(screen, (10, 10, 10),    (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, (60, 0, 0),       (bx, by, bar_w, bar_h))
        fill = (int(255 * (1 - ratio)), int(220 * ratio), 0)  # red → green
        if ratio > 0:
            pygame.draw.rect(screen, fill, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (180, 180, 180),  (bx, by, bar_w, bar_h), 1)

        if DamageNumber.FONT is None:
            DamageNumber.FONT = pygame.font.SysFont(None, 30, bold=True)
        font = pygame.font.SysFont(None, 18)
        txt  = font.render(f"{self.hp}/{self.MAX_HP}", True, (255, 255, 255))
        screen.blit(txt, (bx + bar_w // 2 - txt.get_width() // 2,
                           by + bar_h // 2 - txt.get_height() // 2))