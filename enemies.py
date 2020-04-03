from pathfinding import *
from settings import *
from tilemap import tile_from_xcoords

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, end_x, end_y, speed, hp, image):
        self.groups = game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.screen = game.screen
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pg.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.end_x = end_x
        self.end_y = end_y
        self.last_move = pg.time.get_ticks()
        self.path = game.path.copy()
        self.hp = hp
        self.image = image
        self.load_next_node()

    def update(self):
        passed_time = (pg.time.get_ticks() - self.last_move) / 1000
        self.last_move = pg.time.get_ticks()

        self.x += self.speed * passed_time * self.direction[0]
        self.y += self.speed * passed_time * self.direction[1]

        if ((self.x - self.new_node[0] * TILESIZE) * self.direction[0] >= 0 and (self.y - self.new_node[1] * TILESIZE) *
                self.direction[1] >= 0):
            self.x = self.new_node[0] * TILESIZE
            self.y = self.new_node[1] * TILESIZE
            self.load_next_node()

        self.rect = pg.Rect(self.x, self.y, TILESIZE, TILESIZE)

    def get_hp_rect(self):
        h = 5
        w = self.hp * 2
        x = self.x + (TILESIZE - w) / 2
        y = self.y - 12
        return pg.Rect(x, y, w, h)

    def recreate_path(self):
        self.path = astar(self.game.map.get_map(), (self.new_node[0], self.new_node[1]), (self.end_x, self.end_y))
        self.load_next_node()

    def load_next_node(self):
        if (len(self.path) == 0):
            self.kill()
            return
        self.new_node = self.path.pop(0)
        self.direction = (self.new_node[0] - tile_from_xcoords(self.x), self.new_node[1] - tile_from_xcoords(self.y))
