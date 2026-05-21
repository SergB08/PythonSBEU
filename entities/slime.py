import pygame
import math
import random
import settings
from entities.turret import DamageNumber

DETECT_RANGE    = 400
WALK_SPEED      = 120
RUN_SPEED       = 240
ATTACK_RANGE    = 50
ATTACK_DAMAGE   = 10
ATTACK_COOLDOWN = 1.0
IDLE_TIME_MIN   = 5.0
IDLE_TIME_MAX   = 10.0


class Slime:
    MAX_HP = 60

    def __init__(self, world_x, world_y, frames):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.hp      = self.MAX_HP
        self.alive   = True

        size = 96
        self._frames = [pygame.transform.scale(f, (size, size)) for f in frames]
        self._size   = size

        self._anim_timer = 0.0
        self._anim_frame = 0
        self._anim_speed = 0.15

        self.state        = "idle"
        self._idle_timer  = random.uniform(IDLE_TIME_MIN, IDLE_TIME_MAX)
        self._target_x    = self.world_x
        self._target_y    = self.world_y
        self._room_center = (world_x, world_y)
        self._room_radius = settings.ROOM_SIZE * settings.TILE_SIZE // 2 - settings.TILE_SIZE

        self._attack_timer  = 0.0
        self._angle         = 0.0
        self.damage_numbers = []

    def set_room(self, center_x, center_y):
        self._room_center = (center_x, center_y)

    def _pick_wander_target(self):
        cx, cy = self._room_center
        r = self._room_radius
        self._target_x = cx + random.uniform(-r, r)
        self._target_y = cy + random.uniform(-r, r)

    def take_damage(self, amount, camera_x, camera_y):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y) - self._size // 2 - 10
        self.damage_numbers.append(DamageNumber(sx, sy, amount, (180, 255, 100)))
        if self.hp <= 0:
            self.alive = False

    def _rotate_toward_target(self, tx, ty, dt):
        dx = tx - self.world_x
        dy = ty - self.world_y
        if math.hypot(dx, dy) < 4:
            return
        target_angle = math.degrees(math.atan2(-dy, dx)) #- 90
        diff = (target_angle - self._angle + 180) % 360 - 180
        speed = 180 if self.state == "run" else 90
        step = speed * dt
        if abs(diff) <= step:
            self._angle = target_angle
        else:
            self._angle += math.copysign(step, diff)

    def _move_toward(self, tx, ty, speed, dt, world):
        dx = tx - self.world_x
        dy = ty - self.world_y
        dist = math.hypot(dx, dy)
        if dist < 4:
            return True
        dx /= dist
        dy /= dist
        nx = self.world_x + dx * speed * dt
        ny = self.world_y + dy * speed * dt
        ts = settings.TILE_SIZE
        from level.world import WALL
        def blocked(x, y):
            tx_ = int(x // ts)
            ty_ = int(y // ts)
            h = len(world.tiles)
            w = len(world.tiles[0])
            return (0 <= ty_ < h and 0 <= tx_ < w and
                    world.tiles[ty_][tx_] == WALL)
        if not blocked(nx, self.world_y):
            self.world_x = nx
        if not blocked(self.world_x, ny):
            self.world_y = ny
        return False

    def update(self, dt, player, world):
        if not self.alive:
            return

        self._attack_timer -= dt

        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

        self._anim_timer += dt
        if self._anim_timer >= self._anim_speed:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % len(self._frames)

        px, py  = player.world_x, player.world_y
        dist    = math.hypot(px - self.world_x, py - self.world_y)
        noticed = dist <= DETECT_RANGE

        if self.state == "idle":
            self._idle_timer -= dt
            if noticed:
                self.state = "run"
            elif self._idle_timer <= 0:
                self._pick_wander_target()
                self.state = "wander"

        elif self.state == "wander":
            if noticed:
                self.state = "run"
                return
            self._rotate_toward_target(self._target_x, self._target_y, dt)
            reached = self._move_toward(self._target_x, self._target_y, WALK_SPEED, dt, world)
            if reached:
                self._idle_timer = random.uniform(IDLE_TIME_MIN, IDLE_TIME_MAX)
                self.state = "idle"

        elif self.state == "run":
            if not noticed:
                self.state = "idle"
                self._idle_timer = random.uniform(IDLE_TIME_MIN, IDLE_TIME_MAX)
                return
            self._rotate_toward_target(px, py, dt)
            self._move_toward(px, py, RUN_SPEED, dt, world)
            if dist < ATTACK_RANGE and self._attack_timer <= 0:
                player.body.take_damage_any(ATTACK_DAMAGE)
                self._attack_timer = ATTACK_COOLDOWN

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        if (sx < -self._size or sx > settings.WIDTH + self._size or
                sy < -self._size or sy > settings.HEIGHT + self._size):
            return

        frame   = self._frames[self._anim_frame]
        rotated = pygame.transform.rotate(frame, self._angle)
        screen.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)

        self._draw_health_bar(screen, sx, sy)
        for dn in self.damage_numbers:
            dn.draw(screen)

    def _draw_health_bar(self, screen, sx, sy):
        bar_w = 80
        bar_h = 8
        bx    = sx - bar_w // 2
        by    = sy - self._size // 2 - 14
        ratio = max(0.0, self.hp / self.MAX_HP)
        pygame.draw.rect(screen, (10, 10, 10),    (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, (60, 0, 0),      (bx, by, bar_w, bar_h))
        fill = (int(255 * (1 - ratio)), int(220 * ratio), 0)
        if ratio > 0:
            pygame.draw.rect(screen, fill, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1)
        font = pygame.font.SysFont(None, 18)
        txt  = font.render(f"{int(self.hp)}/{self.MAX_HP}", True, (255, 255, 255))
        screen.blit(txt, (bx + bar_w // 2 - txt.get_width() // 2,
                           by + bar_h // 2 - txt.get_height() // 2))