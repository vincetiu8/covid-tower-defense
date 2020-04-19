from sprites import Obstacle
import math
import pygame as pg
from tilemap import round_to_mtilesize
from pathfinding import heuristic
from settings import TOWER_DATA
from heapq import *

class Projectile(pg.sprite.Sprite):
    def __init__(self, game, x, y, image, speed, lifetime, enemy, damage):
        self.groups = game.projectiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = image.get_size()
        self.x = round_to_mtilesize(x, game.map.tilesize) - self.size[0] / 2
        self.y = round_to_mtilesize(y, game.map.tilesize) - self.size[1] / 2
        self.rect = pg.Rect(self.x, self.y, self.size[0], self.size[1])
        self.image = image
        self.speed = speed
        self.damage = damage
        self.enemy = enemy
        self.end = pg.time.get_ticks() + lifetime * 1000

    def update(self):
        if pg.time.get_ticks() > self.end:
            self.kill()

        if self.enemy.alive():
            self.direction = math.atan2(self.enemy.rect.y - self.y, self.enemy.rect.x - self.x)
        self.rect.x += self.speed * math.cos(self.direction)
        self.rect.y += self.speed * math.sin(self.direction)

        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            hits[0].hp -= self.damage
            self.kill()

class Tower(Obstacle):
    def __init__(self, game, x, y, name):
        super().__init__(game, x, y, game.map.tilesize, game.map.tilesize)
        self.groups = game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.name = name
        self.stage = 0
        self.load_tower_data()

        self.next_spawn = pg.time.get_ticks()
        self.rotation = 0
        self.current_enemy = None

        self.search_for_enemy()

    def load_tower_data(self):
        data = TOWER_DATA[self.name][self.stage]
        self.bullet_spawn_speed = data["bullet_spawn_speed"]
        self.bullet_speed = data["bullet_speed"]
        self.bullet_lifetime = data["bullet_lifetime"]
        self.damage = data["damage"]
        self.range = data["range"]
        self.base_image = data["base_image"]
        self.gun_image = data["gun_image"]
        self.bullet_image = data["bullet_image"]

        if (self.stage < 2):
            data = TOWER_DATA[self.name][self.stage + 1]
            self.upgrade_cost = data["upgrade_cost"]

    def update(self):
        if (pg.time.get_ticks() >= self.next_spawn and self.current_enemy != None):
            enemy_center = self.current_enemy.rect.center
            if (not self.current_enemy.damagable or not self.current_enemy.alive() or heuristic((enemy_center[0], enemy_center[1]), (self.x, self.y)) > self.range):
                self.current_enemy = None
            else:
                temp_x = enemy_center[0]
                temp_y = enemy_center[1]

                if (temp_x - self.x == 0):
                    if (temp_y - self.y > 0):
                        angle = math.pi / 2
                    else:
                        angle = math.pi / 2 * 3

                else:
                    angle = math.atan((temp_y - self.y) / (temp_x - self.x))
                    if (temp_x - self.x < 0):
                        angle += math.pi

                self.rotation = 180 - math.degrees(angle)
                print("yo")
                Projectile(self.game, self.x, self.y, self.bullet_image, self.bullet_speed, self.bullet_lifetime, self.current_enemy, self.damage)
                self.shot = True
                self.next_spawn = pg.time.get_ticks() + self.bullet_spawn_speed * 1000

        if (self.current_enemy == None):
            self.search_for_enemy()
            
    def upgrade(self):
        if self.game.protein >= self.upgrade_cost and self.stage < 2:
            self.game.protein -= self.upgrade_cost
            self.stage += 1
            self.load_tower_data()

    def search_for_enemy(self):
        for enemy in self.game.enemies:
            if (heuristic((enemy.rect.center[0], enemy.rect.center[1]), (self.rect.center[0], self.rect.center[1])) <= self.range and (self.current_enemy == None or enemy.end_dist < self.current_enemy.end_dist)):
                self.current_enemy = enemy
