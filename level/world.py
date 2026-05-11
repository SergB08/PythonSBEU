FLOOR = 0
WALL = 1


class World:
    def __init__(self):
        self.tiles = []
        self.floor_variant = []

        self.spawn_x = 0
        self.spawn_y = 0