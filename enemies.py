from pathfinding import *
from settings import *
import random
from tilemap import tile_from_xcoords, tile_from_coords

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, end_x, end_y, name):
        data = ENEMY_DATA[name]
        self.groups = game.enemies
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.speed = data["speed"]
        self.end_x = end_x
        self.end_y = end_y
        self.last_move = pg.time.get_ticks()
        self.path = game.path.copy()
        self.hp = data["hp"]
        self.dropped_protein = data["protein"]
        self.image = data["image"]
        image_size = self.image.get_size()
        self.rect = pg.Rect(x, y, image_size[0], image_size[1])
        self.direction = [1 if random.random() < 0.5 else -1, 1 if random.random() < 0.5 else -1]
        self.carry_x = 0
        self.carry_y = 0
        self.load_next_node()

    def update(self):
        if (self.hp <= 0):
            self.kill()
            self.game.protein += self.dropped_protein
            return

        passed_time = (pg.time.get_ticks() - self.last_move) / 1000
        self.last_move = pg.time.get_ticks()

        if (self.rect.left <= self.new_node_rect.left):
            self.direction[0] = abs(self.direction[0])

        elif (self.rect.right >= self.new_node_rect.right):
            self.direction[0] = -abs(self.direction[0])

        if (self.rect.top <= self.new_node_rect.top):
            self.direction[1] = abs(self.direction[1])

        elif (self.rect.bottom >= self.new_node_rect.bottom):
            self.direction[1] = -abs(self.direction[1])

        self.carry_x += round(self.speed * passed_time * self.direction[0])
        self.carry_y += round(self.speed * passed_time * self.direction[1])

        if (abs(self.carry_x) >= 1):
            self.rect.x += self.carry_x
            self.carry_x = 0
        if (abs(self.carry_y) >= 1):
            self.rect.y += self.carry_y
            self.carry_y = 0

        if (self.new_node_rect.collidepoint(self.rect.topleft) and self.new_node_rect.collidepoint(self.rect.bottomright)):
            self.load_next_node()

    def get_hp_rect(self):
        h = 5
        w = self.hp * 2
        x = self.rect.x + (self.game.map.tilesize - w) / 2
        y = self.rect.y - 12
        return pg.Rect(x, y, w, h)

    def recreate_path(self):
        self.path = astar(self.game.map.get_map(), (self.new_node[0], self.new_node[1]), (self.end_x, self.end_y))
        self.load_next_node()

    def load_next_node(self):
        if (len(self.path) == 0):
            self.game.lives -= 1
            self.kill()
            return
        self.end_dist = len(self.path)
        self.new_node = self.path.pop(0)
        self.new_node_rect = pg.Rect(self.new_node[0] * self.game.map.tilesize, self.new_node[1] * self.game.map.tilesize, self.game.map.tilesize, self.game.map.tilesize)
