"""
level/safe_room.py

Safe-room interactables: Bed (heal), Chest (Minecraft-style inventory),
Level Portal (enter dungeon). Uses the same floor/wall tiles as regular levels.
"""

import pygame
import settings

INTERACT_RANGE = settings.TILE_SIZE * 2.5


class SafeRoomObject:
    def __init__(self, tile_x, tile_y, label, color, size=None):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.label  = label
        self.color  = color
        self.size   = size or (settings.TILE_SIZE, settings.TILE_SIZE)

    @property
    def world_x(self):
        return self.tile_x * settings.TILE_SIZE + self.size[0] // 2

    @property
    def world_y(self):
        return self.tile_y * settings.TILE_SIZE + self.size[1] // 2

    def near(self, px, py):
        return (abs(px - self.world_x) < INTERACT_RANGE and
                abs(py - self.world_y) < INTERACT_RANGE)

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.tile_x * settings.TILE_SIZE - camera_x)
        sy = int(self.tile_y * settings.TILE_SIZE - camera_y)
        w, h = self.size
        pygame.draw.rect(screen, self.color, (sx, sy, w, h), border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), (sx, sy, w, h), 2, border_radius=8)
        font = pygame.font.SysFont(None, 22, bold=True)
        for i, line in enumerate(self.label.split("\n")):
            lbl = font.render(line, True, (255, 255, 255))
            screen.blit(lbl, (sx + w // 2 - lbl.get_width() // 2,
                               sy + h // 2 - lbl.get_height() // 2 + i * 18))


class Bed(SafeRoomObject):
    def __init__(self, tile_x, tile_y):
        super().__init__(tile_x, tile_y, "BED", (80, 40, 120),
                         (settings.TILE_SIZE * 2, settings.TILE_SIZE))

    def interact(self, player):
        player.heal()          # fully heals all body parts


class ChestObject(SafeRoomObject):
    def __init__(self, tile_x, tile_y):
        super().__init__(tile_x, tile_y, "CHEST", (160, 120, 30),
                         (settings.TILE_SIZE, settings.TILE_SIZE))
        self.is_open = False

    def interact(self, player):
        """Opens the player's ChestUI (Minecraft-style grid)."""
        self.is_open = True
        player.chest_ui.open_chest(player.inventory)

    def draw(self, screen, camera_x, camera_y):
        self.label = "CHEST\n(open)" if self.is_open else "CHEST"
        super().draw(screen, camera_x, camera_y)


class LevelPortal(SafeRoomObject):
    def __init__(self, tile_x, tile_y):
        super().__init__(tile_x, tile_y, "ENTER\nLEVEL", (30, 160, 200),
                         (settings.TILE_SIZE, settings.TILE_SIZE * 2))

    def interact(self, player):
        return "enter_level"


class SafeRoom:
    def __init__(self, world):
        cx = world.spawn_x
        cy = world.spawn_y

        self.bed    = Bed(cx - 4, cy - 1)
        self.chest  = ChestObject(cx + 3, cy - 1)
        self.portal = LevelPortal(cx + 6, cy - 2)
        self.objects = [self.bed, self.chest, self.portal]

        self._heal_msg   = 0.0

    def update(self, dt, player, events):
        if self._heal_msg > 0:
            self._heal_msg -= dt

        # Close chest marker when chest UI closes
        if not player.chest_ui.open:
            self.chest.is_open = False

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                # Don't process world interact if inventory/chest open
                if player.inventory.open or player.chest_ui.open:
                    continue
                for obj in self.objects:
                    if obj.near(player.world_x, player.world_y):
                        result = obj.interact(player)
                        if result == "enter_level":
                            return "enter_level"
                        if isinstance(obj, Bed):
                            self._heal_msg = 2.5

        return None

    def draw(self, screen, camera_x, camera_y, player):
        for obj in self.objects:
            obj.draw(screen, camera_x, camera_y)

        font = pygame.font.SysFont(None, 34, bold=True)
        for obj in self.objects:
            if obj.near(player.world_x, player.world_y):
                if isinstance(obj, Bed):
                    hint = "[E] Sleep & Heal"
                elif isinstance(obj, ChestObject):
                    hint = "[E] Open Chest"
                else:
                    hint = "[E] Enter Level"
                htxt = font.render(hint, True, (255, 255, 100))
                screen.blit(htxt, (settings.WIDTH  // 2 - htxt.get_width()  // 2,
                                   settings.HEIGHT // 2 + 80))

        if self._heal_msg > 0:
            mf  = pygame.font.SysFont(None, 48, bold=True)
            msg = mf.render("Fully healed!", True, (100, 255, 120))
            screen.blit(msg, (settings.WIDTH  // 2 - msg.get_width()  // 2,
                               settings.HEIGHT // 2 - 160))