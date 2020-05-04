import math
import pygame as pg
from data.tilemap import round_to_mtilesize
from data.pathfinding import heuristic
from data.settings import TOWER_DATA
from data.tilemap import *

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.game = game
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect(x, y, w, h)
        for i in range(tile_from_xcoords(w, self.game.map.tilesize)):
            for j in range(tile_from_xcoords(h, self.game.map.tilesize)):
                self.game.map.change_node(tile_from_xcoords(x, self.game.map.tilesize) + i, tile_from_xcoords(y, self.game.map.tilesize) + j, 1)

class Projectile(pg.sprite.Sprite):
    def __init__(self, game, type, x, y, image, speed, lifetime, direction, damage):
        self.groups = game.projectiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.size = image.get_size()
        self.x = round_to_mtilesize(x, game.map.tilesize) - self.size[0] / 2
        self.y = round_to_mtilesize(y, game.map.tilesize) - self.size[1] / 2
        self.rect = pg.Rect(self.x, self.y, self.size[0], self.size[1])
        self.image = image
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.end = pg.time.get_ticks() + lifetime * 1000

    def update(self):
        if pg.time.get_ticks() > self.end:
            self.kill()

        self.rect.x += self.speed * math.cos(self.direction)
        self.rect.y += self.speed * math.sin(self.direction)

        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            if self.type == "basic":
                hits[0].hp -= self.damage
            elif self.type == "slow":
                hits[0].slow()
            self.kill()

class TrackingProjectile(Projectile):
    def __init__(self, game, type, x, y, image, speed, lifetime, direction, damage, enemy):
        super().__init__(game, type, x, y, image, speed, lifetime, direction, damage)
        self.enemy = enemy

    def update(self):
        if self.enemy != None and self.enemy.alive():
            self.direction = math.atan2(self.enemy.rect.center[1] - self.y, self.enemy.rect.center[0] - self.x)
        super().update()

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
        self.directions = data["directions"]
        self.rotating = data["rotating"]
        self.tracking = data["tracking"]
        self.sound = pg.mixer.Sound(data["shoot_sound_path"])

        if (self.stage < 2):
            data = TOWER_DATA[self.name][self.stage + 1]
            self.upgrade_cost = data["upgrade_cost"]

    def update(self):
        if (pg.time.get_ticks() >= self.next_spawn and self.current_enemy != None):
            enemy_center = self.current_enemy.rect.center
            if (not self.current_enemy.damagable or not self.current_enemy.alive() or heuristic((enemy_center[0], enemy_center[1]), (self.rect.x, self.rect.y)) > self.range):
                self.current_enemy = None
            else:
                if self.rotating:
                    temp_x = enemy_center[0]
                    temp_y = enemy_center[1]

                    if (temp_x - self.rect.x == 0):
                        if (temp_y - self.rect.y > 0):
                            angle = math.pi / 2
                        else:
                            angle = math.pi / 2 * 3

                    else:
                        angle = math.atan((temp_y - self.rect.y) / (temp_x - self.rect.x))
                        if (temp_x - self.rect.x < 0):
                            angle += math.pi

                    self.rotation = 180 - math.degrees(angle)

                rotation = self.rotation
                increment = math.pi * 2 / self.directions
                for i in range(self.directions):
                    rotation += increment
                    if self.tracking:
                        type = "basic"
                        if self.name == "goblet_cell":
                            type = "slow"
                        TrackingProjectile(self.game, type, self.rect.x, self.rect.y, self.bullet_image, self.bullet_speed,
                                   self.bullet_lifetime, rotation, self.damage, self.current_enemy)
                    else:
                        Projectile(self.game, "basic", self.rect.x, self.rect.y, self.bullet_image, self.bullet_speed, self.bullet_lifetime, rotation, self.damage)

                self.sound.play()
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
