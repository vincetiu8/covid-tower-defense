from pathfinding import astar
from settings import *
from tilemap import collide_hit_rect, round_to_tilesize, tile_from_coords, tile_from_xcoords

vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Start():
    def __init__(self, game, x, y, w, h, spawn_rate):
        self.game = game
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y
        self.next_spawn = pg.time.get_ticks()
        self.spawn_rate = spawn_rate

    def update(self):
        if (pg.time.get_ticks() >= self.next_spawn):
            Enemy(self.game, self.x, self.y, self.game.goal.x / TILESIZE, self.game.goal.y / TILESIZE)
            self.next_spawn = pg.time.get_ticks() + self.spawn_rate * 1000


class Goal():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, end_x, end_y):
        self.groups = game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.speed = 250
        self.rect = pg.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.end_x = end_x
        self.end_y = end_y
        self.last_move = pg.time.get_ticks()
        self.path = game.path.copy()
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

    def recreate_path(self):
        self.path = astar(self.game.map.get_map(), (self.new_node[0], self.new_node[1]), (self.end_x, self.end_y))
        self.load_next_node()

    def load_next_node(self):
        if (len(self.path) == 0):
            self.kill()
            return
        self.new_node = self.path.pop(0)
        self.direction = (self.new_node[0] - tile_from_xcoords(self.x), self.new_node[1] - tile_from_xcoords(self.y))


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, TILESIZE, TILESIZE)
        print(tile_from_coords(x))
        print(tile_from_coords(y))
        self.game.map.change_node(tile_from_xcoords(x), tile_from_xcoords(y), 1)
