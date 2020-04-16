from sprites import Obstacle
import math
import pygame as pg
from tilemap import round_to_mtilesize
from pathfinding import heuristic
from heapq import *

class Projectile(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, speed, enemy, damage):
        self.groups = game.projectiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = round_to_mtilesize(x, game.map.tilesize) - w / 2
        self.y = round_to_mtilesize(y, game.map.tilesize) - h / 2
        self.w = w
        self.h = h
        self.speed = speed
        self.damage = damage
        self.enemy = enemy

    def update(self):
        self.direction = math.atan2(self.enemy.rect.y - self.y, self.enemy.rect.x - self.x)
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            print(hits[0].rect)
            hits[0].hp -= self.damage
            self.kill()

class Tower(Obstacle):
    def __init__(self, game, x, y, base_images, gun_images, bullet_spawn_speed, bullet_speed, bullet_size, damage, range, upgrade_cost, max_stage):
        super().__init__(game, x, y, game.map.tilesize, game.map.tilesize)
        self.groups = game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.base_images = base_images
        self.gun_images = gun_images
        
        self.bullet_spawn_speed = bullet_spawn_speed
        self.bullet_speed = bullet_speed
        self.bullet_size = bullet_size
        self.damage = damage
        self.range = range
        self.upgrade_cost = upgrade_cost
        self.max_stage = max_stage
        
        self.stage = 0
        self.next_spawn = pg.time.get_ticks()
        self.rotation = 0
        self.current_enemy = None

        self.search_for_enemy()

    def update(self):
        if (pg.time.get_ticks() >= self.next_spawn and self.current_enemy != None):
            enemy_center = self.current_enemy.rect.center
            if (not self.current_enemy.alive() or heuristic((enemy_center[0], enemy_center[1]), (self.x, self.y)) > self.range):
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
                Projectile(self.game, self.x, self.y, self.bullet_size, self.bullet_size, self.bullet_speed, self.current_enemy, self.damage[self.stage])
                self.shot = True
                self.next_spawn = pg.time.get_ticks() + self.bullet_spawn_speed * 1000

        if (self.current_enemy == None):
            self.search_for_enemy()
            
    def upgrade(self):
        if self.game.protein >= self.upgrade_cost and self.stage < self.max_stage:
            self.game.protein -= self.upgrade_cost
            self.stage += 1

    def search_for_enemy(self):
        for enemy in self.game.enemies:
            if (heuristic((enemy.rect.center[0], enemy.rect.center[1]), (self.x, self.y)) <= self.range and (self.current_enemy == None or enemy.end_dist < self.current_enemy.end_dist)):
                self.current_enemy = enemy
