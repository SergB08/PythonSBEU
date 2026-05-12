import pygame
import math
import settings
from level.world import WALL
from entities.turret import PlayerBullet, _angle_to_velocity, DamageNumber


class Player:

    MAX_HP         = 100
    SHOOT_COOLDOWN = 0.20   # seconds between shots

    def __init__(self, idles, animations, rotation_speed=500):

        self.world_x = 0
        self.world_y = 0

        self.width  = 106
        self.height = 62

        self.idle       = idles
        self.animations = animations

        self.anim_count     = 0
        self.angle          = 0
        self.rotation_speed = rotation_speed

        self.hp           = self.MAX_HP
        self.alive        = True
        self._shoot_timer = 0.0
        self.bullets      = []

        self.damage_numbers = []   # floating hit numbers

    # ── angle to mouse ───────────────────────────────────────────────────── #

    def _get_angle_to_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx =  mx - settings.WIDTH  // 2
        dy = -(my - settings.HEIGHT // 2)   # flip: screen-up = positive
        return math.degrees(math.atan2(dy, dx)) - 90

    # ── collision ────────────────────────────────────────────────────────── #

    def collides(self, world, x, y):
        ts = settings.TILE_SIZE
        points = [
            (x - self.width / 2, y - self.height / 2),
            (x + self.width / 2, y - self.height / 2),
            (x - self.width / 2, y + self.height / 2),
            (x + self.width / 2, y + self.height / 2),
        ]
        for px, py in points:
            tx = int(px // ts)
            ty = int(py // ts)
            if world.tiles[ty][tx] == WALL:
                return True
        return False

    # ── combat ───────────────────────────────────────────────────────────── #

    def take_damage(self, amount):
        """Reduce HP and spawn a floating damage number on screen."""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        # Spawn near centre of screen, slightly above the player sprite
        self.damage_numbers.append(
            DamageNumber(
                settings.WIDTH  // 2,
                settings.HEIGHT // 2 - 60,
                amount,
                (255, 50, 50)      # red for player damage
            )
        )
        if self.hp <= 0:
            self.alive = False

    # ── update ───────────────────────────────────────────────────────────── #

    def update(self, keys, dt, world, mouse_buttons):
        if not self.alive:
            return

        speed  = settings.PLAYER_SPEED * dt * 60
        new_x  = self.world_x
        new_y  = self.world_y
        moving = False

        if keys[pygame.K_a]:
            new_x -= speed;  moving = True
        if keys[pygame.K_d]:
            new_x += speed;  moving = True
        if keys[pygame.K_w]:
            new_y -= speed;  moving = True
        if keys[pygame.K_s]:
            new_y += speed;  moving = True

        if not self.collides(world, new_x, self.world_y):
            self.world_x = new_x
        if not self.collides(world, self.world_x, new_y):
            self.world_y = new_y

        if moving:
            self.anim_count += settings.ANIMATION_SPEED * dt * 60
            frames = self.animations["tempWalk"]
            if self.anim_count >= len(frames):
                self.anim_count = 0

        target_angle = self._get_angle_to_mouse()
        if self.rotation_speed == 0:
            self.angle = target_angle
        else:
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * min(1.0, self.rotation_speed * dt)

        # Shooting
        self._shoot_timer -= dt
        if mouse_buttons[0] and self._shoot_timer <= 0:
            self.bullets.append(PlayerBullet(self.world_x, self.world_y, self.angle))
            self._shoot_timer = self.SHOOT_COOLDOWN

        # Bullets
        for b in self.bullets:
            b.update(dt, world)
        self.bullets = [b for b in self.bullets if b.alive]

        # Damage numbers
        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

    # ── draw ─────────────────────────────────────────────────────────────── #

    def draw(self, screen, keys):
        moving = any(keys[k] for k in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s])
        img    = self.animations["tempWalk"][int(self.anim_count)] if moving \
                 else self.idle["tempIdleAnim"]
        rotated = pygame.transform.rotate(img, self.angle)
        rect    = rotated.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
        screen.blit(rotated, rect.topleft)

    def draw_bullets(self, screen, camera_x, camera_y):
        for b in self.bullets:
            b.draw(screen, camera_x, camera_y)

    def draw_hud(self, screen):
        """
        Player HUD — top-left corner.
        Shows: health bar with current/max HP and floating damage numbers.
        """
        PAD   = 20          # distance from screen edge
        bar_w = 260
        bar_h = 28
        bx    = PAD
        by    = PAD
        ratio = max(0.0, self.hp / self.MAX_HP)

        # ── background panel ──
        panel_rect = (bx - 8, by - 8, bar_w + 16, bar_h + 16)
        panel_surf = pygame.Surface((panel_rect[2], panel_rect[3]), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 140))
        screen.blit(panel_surf, (panel_rect[0], panel_rect[1]))

        # ── empty bar ──
        pygame.draw.rect(screen, (70, 0, 0), (bx, by, bar_w, bar_h))

        # ── filled portion: green → yellow → red ──
        fill_color = (int(255 * (1 - ratio)), int(210 * ratio), 0)
        fill_w     = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, fill_color, (bx, by, fill_w, bar_h))

        # ── border ──
        pygame.draw.rect(screen, (210, 210, 210), (bx, by, bar_w, bar_h), 2)

        # ── "HP" label ──
        label_font = pygame.font.SysFont(None, 22, bold=True)
        label      = label_font.render("HP", True, (200, 200, 200))
        screen.blit(label, (bx - label.get_width() - 6,
                             by + bar_h // 2 - label.get_height() // 2))

        # ── numeric HP centred in bar ──
        num_font = pygame.font.SysFont(None, 24, bold=True)
        num_txt  = num_font.render(f"{self.hp}  /  {self.MAX_HP}", True, (255, 255, 255))
        screen.blit(num_txt, (bx + bar_w // 2 - num_txt.get_width()  // 2,
                               by + bar_h // 2 - num_txt.get_height() // 2))

        # ── floating damage numbers (screen-space) ──
        for dn in self.damage_numbers:
            dn.draw(screen)