from sprites import Obstacle
import math
import pygame as pg
from tilemap import round_to_mtilesize
from pathfinding import heuristic
from heapq import *

class Projectile(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, speed, direction, damage):
        self.groups = game.projectiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = round_to_mtilesize(x, game.map.tilesize) - w / 2
        self.y = round_to_mtilesize(y, game.map.tilesize) - h / 2
        self.w = w
        self.h = h
        self.speed = speed
        self.direction = direction
        self.damage = damage

    def update(self):
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            hits[0].hp -= self.damage
            self.kill()

class Tower(Obstacle):
    def __init__(self, game, x, y, w, h, speed, bullet_speed, bullet_size, damage, range):
        super().__init__(game, x, y, w, h)
        self.groups = game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.speed = speed
        self.bullet_speed = bullet_speed
        self.bullet_size = bullet_size
        self.damage = damage
        self.next_spawn = pg.time.get_ticks()
        self.range = range
        self.search_for_enemy()

    def update(self):
        if (pg.time.get_ticks() >= self.next_spawn and self.current_enemy != None):
            if (not self.current_enemy.alive() or heuristic((self.current_enemy.x, self.current_enemy.y), (self.x, self.y)) > self.range):
                self.current_enemy = None
            else:
                temp_x = self.current_enemy.x
                temp_y = self.current_enemy.y

                if (temp_x - self.x == 0):
                    if (temp_y - self.y > 0):
                        angle = math.pi / 2
                    else:
                        angle = math.pi / 2 * 3

                else:
                    angle = math.atan((temp_y - self.y) / (temp_x - self.x))
                    if (temp_x - self.x < 0):
                        angle += math.pi

                Projectile(self.game, self.x, self.y, self.bullet_size, self.bullet_size, self.bullet_speed, angle, self.damage)
                self.next_spawn = pg.time.get_ticks() + self.speed * 1000

        if (self.current_enemy == None):
            self.search_for_enemy()

    def search_for_enemy(self):
        self.current_enemy = None
        for enemy in self.game.enemies:
            if (heuristic((enemy.x, enemy.y), (self.x, self.y)) <= self.range and (self.current_enemy == None or enemy.end_dist < self.current_enemy.end_dist)):
                self.current_enemy = enemy