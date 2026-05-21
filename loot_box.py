import pygame
import random
import math
import settings

### Ящик з припасами, поки що випадають тільки патрони та медикаменти

BOX_HP    = 15     # очки здоров'я ящика
BOX_SIZE  = 48     # розмір для перевірки меж екрану
BOX_SCALE = 96     # розмір текстури при відмальовуванні

class LootBox:
    def __init__(self, world_x, world_y):
        self.world_x  = float(world_x)
        self.world_y  = float(world_y)
        self.hp       = BOX_HP
        self.alive    = True
        self._shaking = 0.0   # таймер візуального тремтіння при попаданні
        self.rotation = random.uniform(0, 360)  # випадковий кут повороту при спавні
        
        from assets import load_lootBox_texture
        self._texture = load_lootBox_texture()
        # кешована повернута текстура щоб не рахувати кожен кадр
        self._cached_rotated = None
        self._cached_angle = None

        self.loot = self._roll_loot()  # заздалегідь визначає що випаде

    def _roll_loot(self):
        # випадково визначає вміст ящика
        from inventory import make_medkit, make_ammo_pistol, make_ai2, make_bandage
        drops = []
        if random.random() < 0.25:
            drops.append(make_medkit())
        ammo_count = random.randint(5, 20)
        if random.random() < 0.3:
            drops.append(make_ammo_pistol(ammo_count))
        if random.random() < 0.50:
            drops.append(make_ai2())
        if random.random() < 0.50:
            drops.append(make_bandage())
        return drops

    def hit(self, damage=1):
        #Викликається при ударі ближнім боєм або кулею. Повертає список предметів якщо знищено
        self._shaking = 0.25
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return self.loot
        return []

    def update(self, dt):
        # зменшує таймер тремтіння з часом
        self._shaking = max(0, self._shaking - dt * 4)

    def _get_rotated_texture(self):
        #Повертає кешовану повернуту текстуру для поточного кута
        if self._cached_rotated is None or self._cached_angle != self.rotation:
            scaled = pygame.transform.scale(self._texture, (BOX_SCALE, BOX_SCALE))
            self._cached_rotated = pygame.transform.rotate(scaled, self.rotation)
            self._cached_angle = self.rotation
        return self._cached_rotated

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.world_x - camera_x)
        sy = int(self.world_y - camera_y)

        # culling - не малювати якщо поза екраном
        if sx < -BOX_SCALE or sx > settings.WIDTH + BOX_SCALE:
            return
        if sy < -BOX_SCALE or sy > settings.HEIGHT + BOX_SCALE:
            return

        # зміщення при тремтінні після попадання
        shake_x = 0
        shake_y = 0
        if self._shaking > 0:
            shake_x = int(math.sin(self._shaking * 80) * 3)
            shake_y = int(math.cos(self._shaking * 80) * 2)

        rotated_texture = self._get_rotated_texture()
        rect = rotated_texture.get_rect(center=(sx + shake_x, sy + shake_y))
        screen.blit(rotated_texture, rect.topleft)