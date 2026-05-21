FLOOR = 0  # прохідна підлога
WALL = 1   # непрохідна стіна


class World:
    def __init__(self):
        self.tiles = []          # двовимірний масив тайлів (FLOOR/WALL)
        self.floor_variant = []  # двовимірний масив варіантів текстури підлоги

        self.spawn_x = 0  # початкова позиція гравця по x (в тайлах)
        self.spawn_y = 0  # початкова позиція гравця по y (в тайлах)

        self.level = 1  # поточний номер рівня

        self.rooms = []  # список центрів кімнат (в тайлах)

        self.ladder_x = None  # позиція виходу по x (в тайлах)
        self.ladder_y = None  # позиція виходу по y (в тайлах)

        self.turret_spawns = []  # список (tile_x, tile_y) де спавняться турелі
        self.turrets = []        # список активних екземплярів турелей
        self.loot_boxes = []     # список активних ящиків з лутом
        self.loot_items = []     # список предметів що лежать на підлозі