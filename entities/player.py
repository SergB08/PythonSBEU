import pygame
import math

import settings
import assets

from level.world import WALL
from entities.turret import PlayerBullet, DamageNumber
from ui.health import BodyHealth
from ui.inventory import InventoryUI, ChestUI

pygame.mixer.init()


# ── Crosshair ────────────────────────────────────────────────────────────────
def draw_crosshair(screen):
    mx, my = pygame.mouse.get_pos()
    color  = (255, 255, 255)
    gap, length, thick = 6, 12, 2
    pygame.draw.line(screen, color, (mx - gap - length, my), (mx - gap, my), thick)
    pygame.draw.line(screen, color, (mx + gap, my),           (mx + gap + length, my), thick)
    pygame.draw.line(screen, color, (mx, my - gap - length),  (mx, my - gap), thick)
    pygame.draw.line(screen, color, (mx, my + gap),           (mx, my + gap + length), thick)
    pygame.draw.circle(screen, color, (mx, my), 2)


class Player:

    SHOOT_COOLDOWN = 0.20
    MAG_SIZE       = 12
    RELOAD_TIME    = 1.5
    SHOOT_SOUND    = None

    def __init__(self, idles, animations, rotation_speed=500):
        self.world_x = 0
        self.world_y = 0
        self.width   = 106
        self.height  = 62

        self.idle       = idles
        self.animations = animations
        self.anim_count = 0
        self.angle      = 0
        self.rotation_speed = rotation_speed

        # ── New health system ──────────────────────────────────────────
        self.body = BodyHealth()

        # Legacy shim so game.py `player.alive` still works
        @property
        def alive(self):
            return self.body.alive

        # ── Inventory + chest ─────────────────────────────────────────
        self.inventory = InventoryUI()
        self.chest_ui  = ChestUI()

        # Weapon / ammo
        self.weapon        = "pistol"
        self.ammo          = self.MAG_SIZE
        self._reloading    = False
        self._reload_timer = 0.0
        self._shoot_timer  = self.SHOOT_COOLDOWN * 3

        self.bullets        = []
        self.damage_numbers = []   # kept for turret hit numbers on screen

        if Player.SHOOT_SOUND is None:
            Player.SHOOT_SOUND = pygame.mixer.Sound(assets.PlayerPistolShot)

    # ── alive shim ───────────────────────────────────────────────────────── #
    @property
    def alive(self):
        return self.body.alive

    # ── legacy HP shim (game.py reads player.hp) ─────────────────────────── #
    @property
    def hp(self):
        return int(self.body.total_hp)

    @hp.setter
    def hp(self, value):
        # scale all parts proportionally when set externally (level transition)
        ratio = max(0.0, value / self.body.max_total_hp)
        for part in self.body.parts.values():
            part.hp = ratio * 100

    # ── helpers ──────────────────────────────────────────────────────────── #

    def _get_angle_to_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx =  mx - settings.WIDTH  // 2
        dy =  my - settings.HEIGHT // 2
        return -(math.degrees(math.atan2(dy, dx)) + 90)

    def collides(self, world, x, y):
        ts = settings.TILE_SIZE
        for px, py in [
            (x - self.width / 2, y - self.height / 2),
            (x + self.width / 2, y - self.height / 2),
            (x - self.width / 2, y + self.height / 2),
            (x + self.width / 2, y + self.height / 2),
        ]:
            tx, ty = int(px // ts), int(py // ts)
            if 0 <= ty < len(world.tiles) and 0 <= tx < len(world.tiles[0]):
                if world.tiles[ty][tx] == WALL:
                    return True
        return False

    # ── combat ───────────────────────────────────────────────────────────── #

    def take_damage(self, amount, part="Torso"):
        self.body.take_damage(amount, part)
        # floating damage number on screen
        self.damage_numbers.append(
            DamageNumber(settings.WIDTH // 2, settings.HEIGHT // 2 - 60,
                         amount, (255, 50, 50))
        )

    def heal(self, amount=9999):
        self.body.heal_all(amount)

    def start_reload(self):
        if not self._reloading and self.ammo < self.MAG_SIZE:
            self._reloading    = True
            self._reload_timer = self.RELOAD_TIME

    # ── update ───────────────────────────────────────────────────────────── #

    def update(self, keys, dt, world, mouse_buttons, events=None):
        if not self.alive:
            return

        self.body.update(dt)

        # ── key events ────────────────────────────────────────────────────
        if events:
            for e in events:
                # Inventory / health panel toggle
                self.inventory.handle_event(e)
                self.chest_ui.handle_event(e)

                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_i, pygame.K_TAB):
                        self.inventory.toggle()
                    elif e.key == pygame.K_h:
                        self.body.toggle_panel()
                    elif e.key == pygame.K_1:
                        self.weapon = "pistol"
                    elif e.key == pygame.K_2:
                        self.weapon = "melee"
                    elif e.key == pygame.K_r:
                        self.start_reload()

        # ── movement ──────────────────────────────────────────────────────
        speed  = settings.PLAYER_SPEED * dt * 60
        dx, dy = 0, 0
        moving = False
        if keys[pygame.K_a]: dx -= 1; moving = True
        if keys[pygame.K_d]: dx += 1; moving = True
        if keys[pygame.K_w]: dy -= 1; moving = True
        if keys[pygame.K_s]: dy += 1; moving = True

        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length; dy /= length

        new_x = self.world_x + dx * speed
        new_y = self.world_y + dy * speed

        if moving:
            self.anim_count += settings.ANIMATION_SPEED * dt * 60
            if self.anim_count >= len(self.animations["tempWalk"]):
                self.anim_count = 0

        if not self.collides(world, new_x, self.world_y): self.world_x = new_x
        if not self.collides(world, self.world_x, new_y): self.world_y = new_y

        self.angle = self._get_angle_to_mouse()

        # ── reload ────────────────────────────────────────────────────────
        if self._reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self.ammo       = self.MAG_SIZE
                self._reloading = False

        # ── shoot ─────────────────────────────────────────────────────────
        self._shoot_timer -= dt
        if (self.weapon == "pistol"
                and mouse_buttons[0]
                and self._shoot_timer <= 0
                and not self._reloading
                and not self.inventory.open
                and not self.chest_ui.open):
            if self.ammo > 0:
                mx, my = pygame.mouse.get_pos()
                dx2 =  mx - settings.WIDTH  // 2
                dy2 =  my - settings.HEIGHT // 2
                shoot_angle = math.degrees(math.atan2(-dy2, dx2)) - 90
                self.bullets.append(PlayerBullet(self.world_x, self.world_y, shoot_angle))
                self.ammo -= 1
                self._shoot_timer = self.SHOOT_COOLDOWN
                Player.SHOOT_SOUND.set_volume(settings.VOLUME)
                Player.SHOOT_SOUND.play()
            else:
                self.start_reload()

        # ── bullets ───────────────────────────────────────────────────────
        for b in self.bullets: b.update(dt, world)
        self.bullets = [b for b in self.bullets if b.alive]

        for dn in self.damage_numbers: dn.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

    # ── draw ─────────────────────────────────────────────────────────────── #

    def draw(self, screen, keys):
        moving = any(keys[k] for k in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s])
        img = (self.animations["tempWalk"][int(self.anim_count)]
               if moving else self.idle["tempIdleAnim"])
        rotated = pygame.transform.rotate(img, self.angle)
        rect    = rotated.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
        screen.blit(rotated, rect.topleft)
        self._draw_body_hp(screen, rect)

    def _draw_body_hp(self, screen, sprite_rect):
        """Thin HP bar above the sprite, coloured by overall health."""
        bar_w, bar_h = 60, 6
        bx = sprite_rect.centerx - bar_w // 2
        by = sprite_rect.top - 12
        ratio = max(0.0, self.body.overall_ratio)
        col = ((int(255 * (1 - ratio)), int(210 * ratio), 0))
        pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h))
        if ratio > 0:
            pygame.draw.rect(screen, col, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1)

    def draw_bullets(self, screen, camera_x, camera_y):
        for b in self.bullets:
            b.draw(screen, camera_x, camera_y)

    def draw_hud(self, screen):
        """
        Main HUD: overall HP bar (top-left) + ammo + weapon.
        Per-limb bars and moodles drawn by body.draw().
        Inventory drawn by inventory.draw() / chest_ui.draw().
        """
        PAD   = 20
        bar_w = 260
        bar_h = 28
        bx, by = PAD, PAD
        ratio  = max(0.0, self.body.overall_ratio)

        # Overall HP panel
        panel = pygame.Surface((bar_w + 16, bar_h + 16), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        screen.blit(panel, (bx - 8, by - 8))
        pygame.draw.rect(screen, (70, 0, 0),         (bx, by, bar_w, bar_h))
        fill_col = (int(255 * (1 - ratio)), int(210 * ratio), 0)
        if ratio > 0:
            pygame.draw.rect(screen, fill_col,       (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (210, 210, 210),    (bx, by, bar_w, bar_h), 2)

        lf = pygame.font.SysFont(None, 22, bold=True)
        nf = pygame.font.SysFont(None, 24, bold=True)
        lbl = lf.render("HP", True, (200, 200, 200))
        num = nf.render(f"{int(self.body.total_hp)} / {self.body.max_total_hp}",
                        True, (255, 255, 255))
        screen.blit(lbl, (bx - lbl.get_width() - 6, by + bar_h // 2 - lbl.get_height() // 2))
        screen.blit(num, (bx + bar_w // 2 - num.get_width() // 2,
                          by + bar_h // 2 - num.get_height() // 2))

        # Body-part bars + moodles
        self.body.draw(screen)

        # Weapon / ammo row  (placed below moodle area — far right bottom)
        af = pygame.font.SysFont(None, 34, bold=True)
        wf = pygame.font.SysFont(None, 24, bold=True)
        wx = settings.WIDTH - 260
        wy = settings.HEIGHT - 70
        wlbl = wf.render(f"{'PISTOL' if self.weapon == 'pistol' else 'MELEE'}   "
                         f"[1] Pistol  [2] Melee", True, (180, 180, 180))
        screen.blit(wlbl, (wx, wy))
        if self.weapon == "pistol":
            if self._reloading:
                pct  = 1.0 - self._reload_timer / self.RELOAD_TIME
                rtxt = af.render(f"Reloading {int(pct * 100)}%", True, (255, 200, 50))
                screen.blit(rtxt, (wx, wy + 24))
            else:
                atxt = af.render(f"{self.ammo} / {self.MAG_SIZE}   [R] Reload",
                                 True, (255, 255, 255))
                screen.blit(atxt, (wx, wy + 24))

        # Hints
        hf = pygame.font.SysFont(None, 22)
        screen.blit(hf.render("[I]/[Tab] Inventory   [H] Health", True, (130, 130, 140)),
                    (PAD, settings.HEIGHT - 26))

        # Floating damage numbers
        for dn in self.damage_numbers:
            dn.draw(screen)

        # Inventory & chest on top of everything
        self.inventory.draw(screen)
        self.chest_ui.draw(screen)