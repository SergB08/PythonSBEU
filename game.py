# game.py
import pygame
from level import world
import settings
import controls
from entities.player import Player, draw_crosshair
from entities.turret import Turret
from level.generation import generate_world, generate_safe_room_world
from level.rendering import draw_world, draw_minimap
from assets import load_player_sprites2, load_turret_sprites
from level.safe_room import SafeRoom
import random, math
from death_screen import DeathScreen

_death_screen = None   # lazy singleton


# ─────────────────────────────────────────────────────────────────────────────
#  PAUSE MENU
# ─────────────────────────────────────────────────────────────────────────────

class PauseMenu:
    def __init__(self):
        from assets import load_menu_textures
        from main_menu import Button
        tex_idle, tex_hover, tex_click = load_menu_textures()
        self._Button       = Button
        self._textures     = (tex_idle, tex_hover, tex_click)
        self.font_big      = pygame.font.SysFont(None, 100, bold=True)
        self.font_btn      = pygame.font.SysFont(None, 30,  bold=True)
        self._build()

    def _build(self):
        from main_menu import Button
        tex_idle, tex_hover, tex_click = self._textures
        bw, bh = 320, 80
        cx = settings.WIDTH  // 2 - bw // 2
        cy = settings.HEIGHT // 2 - 40
        self.buttons = {
            "resume": Button(cx, cy,       bw, bh, "RESUME",    self.font_btn, tex_idle, tex_hover, tex_click),
            "menu":   Button(cx, cy + 120, bw, bh, "MAIN MENU", self.font_btn, tex_idle, tex_hover, tex_click),
        }

    def run(self, screen, events):
        """
        Returns 'resume', 'menu', or None.
        NOTE: caller must NOT pass the ESC KEYDOWN event that opened the
        pause menu — consume it first so this method never sees it.
        """
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        title = self.font_big.render("PAUSED", True, (200, 200, 220))
        screen.blit(title, (settings.WIDTH  // 2 - title.get_width()  // 2,
                            settings.HEIGHT // 2 - 200))

        for name, btn in self.buttons.items():
            if btn.update(events):
                return name
            btn.draw(screen)

        # ESC while paused = resume
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "resume"

        return None


_pause_menu: PauseMenu | None = None


def _get_pause_menu() -> PauseMenu:
    global _pause_menu
    if _pause_menu is None:
        _pause_menu = PauseMenu()
    return _pause_menu


# ─────────────────────────────────────────────────────────────────────────────

def init_game(floor_tiles):
    playerLegsIdleAnim, playerLegsWalkAnim, playerHead, playerBody, playerBodyPistol = load_player_sprites2()
    w      = generate_world(len(floor_tiles))
    player = Player(playerHead, playerBody, playerBodyPistol,
                    playerLegsIdleAnim["legsIdleAnim"],
                    playerLegsWalkAnim["legsWalkAnim"])
    player.world_x = w.spawn_x * settings.TILE_SIZE
    player.world_y = w.spawn_y * settings.TILE_SIZE

    legs, head_idle, head_angry, head_cautious = load_turret_sprites()
    w.turrets = []
    for i, (tx, ty) in enumerate(w.turret_spawns):
        # tx, ty are room centers in tile coords
        # pick a random floor tile within that room's bounds
        room_pos = list(w.rooms)[i] if i < len(w.rooms) else None

        # random offset within the room interior (avoid walls near edge)
        margin = 0  # tiles from room edge
        half = settings.ROOM_SIZE // 2 - margin

        for _ in range(50):  # try up to 50 times
            ox = random.randint(-half, half)
            oy = random.randint(-half, half)
            candidate_tx = tx + ox
            candidate_ty = ty + oy
            if (0 <= candidate_ty < len(w.tiles) and
                    0 <= candidate_tx < len(w.tiles[0]) and
                    w.tiles[candidate_ty][candidate_tx] == FLOOR):
                spawn_x = candidate_tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
                spawn_y = candidate_ty * settings.TILE_SIZE + settings.TILE_SIZE // 2
                break
        else:
            # fallback: use center
            spawn_x = tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
            spawn_y = ty * settings.TILE_SIZE + settings.TILE_SIZE // 2

        # rotate toward room center + deviation
        cx = tx * settings.TILE_SIZE + settings.TILE_SIZE // 2
        cy = ty * settings.TILE_SIZE + settings.TILE_SIZE // 2
        dx = cx - spawn_x
        dy = cy - spawn_y
        if abs(dx) < 1 and abs(dy) < 1:
            toward_center = random.uniform(0, 360)
        else:
            toward_center = math.degrees(math.atan2(dy, dx)) + 180
        deviation = random.uniform(-15, 15)
        initial_angle = toward_center + deviation
        #print(initial_angle)
        

        w.turrets.append(Turret(
            spawn_x, spawn_y,
            legs, head_idle, head_cautious, head_angry,
            initial_angle=initial_angle
    ))

    return w, player


from level.world import FLOOR


def init_safe_room(floor_tiles, existing_player=None):
    playerLegsIdleAnim, playerLegsWalkAnim, playerHead, playerBody, playerBodyPistol = load_player_sprites2()
    w = generate_safe_room_world(len(floor_tiles))

    if existing_player is None:
        player = Player(playerHead, playerBody, playerBodyPistol,
                        playerLegsIdleAnim["legsIdleAnim"],
                        playerLegsWalkAnim["legsWalkAnim"])
    else:
        player = existing_player
        player.bullets = []

    player.world_x = w.spawn_x * settings.TILE_SIZE
    player.world_y = w.spawn_y * settings.TILE_SIZE

    safe_room = SafeRoom(w)
    return w, player, safe_room


# ── per-scene pause flags (module-level so they survive between frames) ────
_safe_room_paused = False
_game_paused      = False


# ─────────────────────────────────────────────────────────────────────────────
#  SAFE ROOM
# ─────────────────────────────────────────────────────────────────────────────

def run_safe_room(screen, dt, events, world, player, safe_room,
                  floor_tiles, wall_tiles, ladder_img):
    global _safe_room_paused

    keys = pygame.key.get_pressed()

    # ── Split events: consume ESC for pause toggle, pass rest normally ── #
    esc_pressed    = False
    filtered_events = []
    for e in events:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            esc_pressed = True   # consumed here — NOT forwarded
        else:
            filtered_events.append(e)

    if esc_pressed and not _safe_room_paused:
        # Open pause — don't forward ESC to PauseMenu this frame
        _safe_room_paused = True
        esc_pressed = False   # already handled

    camera_x = player.world_x - settings.WIDTH  // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
    draw_minimap(screen, world, player)

    result = None
    if not _safe_room_paused:
        result = safe_room.update(dt, player, filtered_events)
        safe_room.draw(screen, camera_x, camera_y, player)
        player.update(keys, dt, world, pygame.mouse.get_pressed(), filtered_events)
        player.draw(screen, keys, dt)
        player.draw_bullets(screen, camera_x, camera_y)
        player.draw_hud(screen)
    else:
        safe_room.draw(screen, camera_x, camera_y, player)
        player.draw(screen, keys, dt)
        player.draw_hud(screen)

    draw_crosshair(screen)

    font = pygame.font.SysFont(None, 40, bold=True)
    lbl  = font.render("SAFE ROOM", True, (150, 220, 255))
    screen.blit(lbl, (settings.WIDTH // 2 - lbl.get_width() // 2, 30))

    if _safe_room_paused:
        # Pass filtered_events (no ESC in them) so PauseMenu ESC = resume only
        pm_result = _get_pause_menu().run(screen, filtered_events)
        if pm_result == "resume":
            _safe_room_paused = False
        elif pm_result == "menu":
            _safe_room_paused = False
            return "menu", world, player, safe_room
        return "safe_room", world, player, safe_room

    if result == "enter_level":
        new_world, new_player = init_game(floor_tiles)
        new_world.level = 1
        new_player.hp   = player.hp
        return "playing", new_world, new_player, safe_room

    return "safe_room", world, player, safe_room


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN GAME LEVEL
# ─────────────────────────────────────────────────────────────────────────────

def run_game(screen, dt, events, world, player, floor_tiles, wall_tiles, ladder_img,
             safe_room=None):
    global _game_paused, _death_screen

    keys          = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    # ── Split events: consume ESC for pause toggle ────────────────────── #
    esc_pressed     = False
    filtered_events = []
    for e in events:
        if (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
                and player and player.alive):
            esc_pressed = True   # consumed — NOT forwarded
        else:
            filtered_events.append(e)

    if esc_pressed and not _game_paused:
        _game_paused = True
        esc_pressed  = False

    # ── Paused ────────────────────────────────────────────────────────── #
    if _game_paused:
        camera_x = player.world_x - settings.WIDTH  // 2
        camera_y = player.world_y - settings.HEIGHT // 2
        draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
        draw_minimap(screen, world, player)
        player.draw(screen, keys, dt)
        player.draw_bullets(screen, camera_x, camera_y)
        for turret in world.turrets:
            turret.draw(screen, camera_x, camera_y)
        player.draw_hud(screen)
        draw_crosshair(screen)

        # Pass filtered_events so PauseMenu ESC = resume (not re-open)
        pm_result = _get_pause_menu().run(screen, filtered_events)
        if pm_result == "resume":
            _game_paused = False
        elif pm_result == "menu":
            _game_paused = False
            return "menu", world, player, safe_room
        return "playing", world, player, safe_room

    # ── Normal logic ──────────────────────────────────────────────────── #

    near_ladder         = False
    near_ladder_blocked = False
    all_turrets_dead    = all(not t.alive for t in world.turrets)

    if world.ladder_x is not None:
        dx    = player.world_x - (world.ladder_x * settings.TILE_SIZE + settings.TILE_SIZE * 2)
        dy    = player.world_y - (world.ladder_y * settings.TILE_SIZE + settings.TILE_SIZE * 2)
        close = abs(dx) < settings.TILE_SIZE * 2 and abs(dy) < settings.TILE_SIZE * 2
        near_ladder         = close and all_turrets_dead
        near_ladder_blocked = close and not all_turrets_dead

    if player.alive:
        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if event.key == controls.INTERACT_KEY and near_ladder:
                    next_level    = world.level + 1
                    new_world, new_player = init_game(floor_tiles)
                    new_world.level = next_level
                    new_player.hp   = player.hp
                    new_player.ammo = player.ammo
                    return "playing", new_world, new_player, safe_room

        player.update(keys, dt, world, mouse_buttons, filtered_events)

    camera_x = player.world_x - settings.WIDTH  // 2
    camera_y = player.world_y - settings.HEIGHT // 2

    draw_world(screen, world, floor_tiles, wall_tiles, ladder_img, camera_x, camera_y)
    draw_minimap(screen, world, player)
    player.draw(screen, keys, dt)
    player.draw_bullets(screen, camera_x, camera_y)

    if near_ladder_blocked:
        font = pygame.font.SysFont(None, 40, bold=True)
        text = font.render("Eliminate all enemies first!", True, (255, 80, 80))
        screen.blit(text, (settings.WIDTH  // 2 - text.get_width()  // 2,
                            settings.HEIGHT // 2 - 100))
    if near_ladder:
        font = pygame.font.SysFont(None, 40, bold=True)
        text = font.render("[E] Enter next level", True, (100, 255, 120))
        screen.blit(text, (settings.WIDTH  // 2 - text.get_width()  // 2,
                            settings.HEIGHT // 2 - 100))

    if player.alive:
        # Turrets update and shoot only while player is alive
        for turret in world.turrets:
            turret.update(dt, player, world)
            turret.draw(screen, camera_x, camera_y)

            for bullet in turret.bullets:
                if bullet.alive:
                    dx = bullet.x - player.world_x
                    dy = bullet.y - player.world_y
                    if abs(dx) < 30 and abs(dy) < 30:
                        # Random body-part hit with weights
                        player.body.take_damage_any(bullet.DAMAGE)
                        bullet.alive = False

            for bullet in player.bullets:
                if bullet.alive:
                    for turret in world.turrets:
                        if not turret.alive:
                            continue
                        dx = bullet.x - turret.world_x
                        dy = bullet.y - turret.world_y
                        if abs(dx) < 60 and abs(dy) < 60:
                            turret.take_damage(bullet.DAMAGE, camera_x, camera_y)
                            bullet.alive = False
    else:
        # Player dead — draw turrets frozen, no updates
        for turret in world.turrets:
            turret.draw(screen, camera_x, camera_y)

    player.draw_hud(screen)
    draw_crosshair(screen)

    # ── Death screen ──────────────────────────────────────────────────── #
    if not player.alive:
        if _death_screen is None:
            _death_screen = DeathScreen()
        result = _death_screen.run(screen, events)  # use original events here
        if result == "restart":
            new_world, new_player = init_game(floor_tiles)
            return "playing", new_world, new_player, safe_room
        if result == "menu":
            return "menu", None, None, None

    return "playing", world, player, safe_room