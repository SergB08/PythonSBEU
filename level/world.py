FLOOR = 0
WALL = 1


class World:
    def __init__(self):

        self.tiles = []
        self.floor_variant = []

        self.spawn_x = 0
        self.spawn_y = 0

        self.level = 1

        self.rooms = []

        self.ladder_x = None
        self.ladder_y = None

        # List of (tile_x, tile_y) where turrets should be placed
        self.turret_spawns = []
        self.turrets = []
        self.loot_boxes = []
        self.loot_items = []