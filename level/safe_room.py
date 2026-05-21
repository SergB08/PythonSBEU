import pygame
import settings

INTERACT_RANGE = settings.TILE_SIZE * 1.25  # відстань для взаємодії з об'єктом


class SafeRoomObject:
    def __init__(self, tile_x, tile_y, label, color, size=None):
        self.tile_x = tile_x  # позиція об'єкта по x (в тайлах)
        self.tile_y = tile_y  # позиція об'єкта по y (в тайлах)
        self.label  = label   # підпис на об'єкті
        self.color  = color   # колір прямокутника об'єкта
        self.size   = size or (settings.TILE_SIZE, settings.TILE_SIZE)  # розмір в пікселях

    @property
    def world_x(self):
        # центр об'єкта по Х у світових координатах
        return self.tile_x * settings.TILE_SIZE + self.size[0] // 2

    @property
    def world_y(self):
        # центр об'єкта по У у світових координатах
        return self.tile_y * settings.TILE_SIZE + self.size[1] // 2

    def near(self, px, py):
        # перевіряє чи гравець достатньо близько для взаємодії
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
        # повністю лікує всі частини тіла гравця
        player.heal()


class ChestObject(SafeRoomObject):
    def __init__(self, tile_x, tile_y):
        super().__init__(tile_x, tile_y, "CHEST", (160, 120, 30),
                         (settings.TILE_SIZE, settings.TILE_SIZE))
        self.is_open = False

    def interact(self, player):
        # відкриває інтерфейс скрині у стилі Minecraft
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
        # повертає сигнал для переходу на рівень
        return "enter_level"


class SafeRoom:
    def __init__(self, world):
        cx = world.spawn_x
        cy = world.spawn_y

        # розміщення інтерактивних об'єктів відносно точки спавну
        self.bed    = Bed(cx - 6, cy - 4)
        self.chest  = ChestObject(cx + 0, cy - -3)
        self.portal = LevelPortal(cx + 5, cy - 2)
        self.objects = [self.bed, self.portal]  # скриня тимчасово прихована

        self._heal_msg = 0.0  # таймер повідомлення про лікування

    def update(self, dt, player, events):
        if self._heal_msg > 0:
            self._heal_msg -= dt

        # закриваємо маркер скрині коли UI закривається
        if not player.chest_ui.open:
            self.chest.is_open = False

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                # не обробляємо взаємодію якщо відкритий інвентар або скриня
                if player.inventory.open or player.chest_ui.open:
                    continue
                for obj in self.objects:
                    if obj.near(player.world_x, player.world_y):
                        result = obj.interact(player)
                        if result == "enter_level":
                            return "enter_level"
                        if isinstance(obj, Bed):
                            self._heal_msg = 2.5  # показуємо повідомлення 2.5 секунди

        return None

    def draw(self, screen, camera_x, camera_y, player):
        # малює всі об'єкти кімнати
        for obj in self.objects:
            obj.draw(screen, camera_x, camera_y)

        # підказка взаємодії коли гравець поруч
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

        # повідомлення про успішне лікування
        if self._heal_msg > 0:
            mf  = pygame.font.SysFont(None, 48, bold=True)
            msg = mf.render("Fully healed!", True, (100, 255, 120))
            screen.blit(msg, (settings.WIDTH  // 2 - msg.get_width()  // 2,
                               settings.HEIGHT // 2 - 160))