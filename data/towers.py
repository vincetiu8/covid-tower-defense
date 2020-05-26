import math
import pygame as pg
from data.tilemap import round_to_mtilesize
from data.pathfinding import heuristic, manhattan
from data.settings import TOWER_DATA
from data.tilemap import *
from data.game_misc import Explosion

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
    def __init__(self, args):
        self.groups = args[0].projectiles
        self.clock = args[0].clock
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = args[0]
        self.type = type
        self.size = args[3].get_size()
        self.rect = pg.Rect(args[1], args[2], self.size[0], self.size[1])
        self.rect.centerx = args[1]
        self.rect.centery = args[2]
        self.raw_image = args[3]
        self.image = self.raw_image.copy()
        self.speed = args[4]
        self.slow_speed = args[6]
        self.slow_duration = args[7]
        self.damage = args[9]
        self.direction = args[8]
        pg.transform.rotate(self.image, args[8])
        self.shield_damage = args[10]
        self.time_passed = 0
        self.carry = 0
        self.end = args[5] * 1000

    def update(self):
        if self.time_passed > self.end:
            self.kill()

        self.delta = self.clock.get_time()
        self.time_passed += self.delta
        self.delta /= 1000
        self.carry += self.delta
        if self.carry >= 1 / self.speed:
            self.rect.centerx -= round(self.carry * self.speed * math.sin(self.direction))
            self.rect.centery -= round(self.carry * self.speed * math.cos(self.direction))
            self.carry = 0

        self.check_for_impact()

    def check_for_impact(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            hits[0].damage(self.damage, self.shield_damage)
            if self.slow_speed != 1:
                hits[0].slow(self.slow_speed, self.slow_duration)
            self.kill()

class TrackingProjectile(Projectile):
    def __init__(self, args):
        Projectile.__init__(self, args[:-3])
        self.rotation_speed = math.radians(args[-3])
        self.range = args[-2]
        self.enemy = args[-1]

    def update(self):
        if self.enemy != None:
            enemy_center = self.enemy.rect.center
            if (not self.enemy.damagable or not self.enemy.alive() or heuristic(
                    enemy_center, self.rect.center) > self.range):
                self.enemy = None

            else:
                temp_x = enemy_center[0]
                temp_y = enemy_center[1]

                if (temp_y - self.rect.centery == 0):
                    if (temp_x - self.rect.centerx > 0):
                        direction = math.pi * 3 / 2
                    else:
                        direction = math.pi / 2

                else:
                    direction = math.atan((temp_x - self.rect.centerx) / (temp_y - self.rect.centery))
                    if (temp_y - self.rect.centery > 0):
                        direction += math.pi

                if direction - self.direction > math.pi:
                    direction -= math.pi * 2

                elif direction - self.direction < -math.pi:
                    direction += math.pi * 2

                if direction - self.direction > self.rotation_speed:
                    self.direction += self.rotation_speed
                    self.direction %= 2 * math.pi
                elif direction - self.direction < -self.rotation_speed:
                    self.direction -= self.rotation_speed
                    self.direction %= 2 * math.pi
                else:
                    self.direction = direction
                    self.direction %= 2 * math.pi
                self.image = pg.transform.rotate(self.raw_image, math.degrees(self.direction))

        if self.enemy == None:
            self.search_for_enemy()

        super().update()

    def search_for_enemy(self):
        if self.enemy != None:
            enemy_her = heuristic(self.enemy.rect.center, self.rect.center)

        for enemy in self.game.enemies:
            t_enemy_her = heuristic(enemy.rect.center, self.rect.center)
            if self.enemy == None or t_enemy_her < enemy_her:
                self.enemy = enemy
                enemy_her = t_enemy_her

class ExplodingProjectile(Projectile):
    def __init__(self, args):
        Projectile.__init__(self, args[:-1])
        self.explosion_radius = args[-1]

    def check_for_impact(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            center = self.rect.center
            self.rect.width = self.rect.height = self.explosion_radius
            self.rect.center = center
            hits = pg.sprite.spritecollide(self, self.game.enemies, False)
            Explosion(self.game, self.rect.center[0], self.rect.center[1], self.explosion_radius)
            for hit in hits:
                hit.damage(self.damage, self.shield_damage)
                if self.slow_speed != 1:
                    hit.slow(self.slow_speed, self.slow_duration)
            self.kill()

class TrackingExplodingProjectile(TrackingProjectile, ExplodingProjectile):
    def __init__(self, args):
        TrackingProjectile.__init__(self, args[:-1])
        self.explosion_radius = args[-1]

class Tower(Obstacle):
    def __init__(self, game, x, y, name):
        super().__init__(game, x, y, game.map.tilesize, game.map.tilesize)
        self.groups = game.towers
        self.clock = game.clock
        pg.sprite.Sprite.__init__(self, self.groups)
        self.name = name
        self.stage = 0
        self.load_tower_data()

        self.time_passed = 0
        self.next_spawn = 1
        
        self.rotation = 0
        self.current_enemy = None
        
        self.buffs = {
            "damage": 0,
            "range": 0
        }

        self.search_for_enemy(self.range)

    def load_tower_data(self):
        data = TOWER_DATA[self.name]["stages"][self.stage]
        self.range = data["range"]
        self.base_image = data["base_image"]
        self.area_of_effect = data["area_of_effect"]
            
        load_attack_attrs = True # always load unless self.area_of_effect and self.aoe_buff

        if self.area_of_effect:
            self.aoe_sprite = pg.sprite.Sprite()
            self.aoe_sprite.rect = self.rect.copy()
            self.update_aoe_sprite(self.range)
            self.aura_color = data["aura_color"]
            self.aoe_buff = data["aoe_buff"]
            
            if self.aoe_buff:
                aoe_buff_types = ["damage", "range"]
                load_attack_attrs = False
                self.aoe_buff_type = aoe_buff_types[data["aoe_buff_type"]]
                self.aoe_buff_amount = data["aoe_buff_amount"]
        else:
            self.bullet_speed = data["bullet_speed"]
            self.bullet_lifetime = data["bullet_lifetime"]
            self.rotating = data["rotating"]
            self.tracking = data["tracking"]
            self.bullet_image = data["bullet_image"]
            self.directions = data["directions"]
            if self.rotating:
                self.gun_image = data["gun_image"]
                self.rotation_speed = data["rotation_speed"]

            self.explode_on_impact = data["explode_on_impact"]
            if self.explode_on_impact:
                self.explosion_radius = data["explosion_radius"]
                
        if load_attack_attrs:
            self.slow_speed = data["slow_speed"]
            self.slow_duration = data["slow_duration"]
            self.damage = data["damage"]
            self.different_shield_damage = data["different_shield_damage"]
            self.sound = data["shoot_sound"]
            self.attack_speed = data["attack_speed"]
            
            if self.different_shield_damage:
                self.shield_damage = data["shield_damage"]
            else:
                self.shield_damage = self.damage

        if (self.stage < 2):
            data = TOWER_DATA[self.name]["stages"][self.stage + 1]
            self.upgrade_cost = data["upgrade_cost"]

    def update(self):
        true_range = self.range + self.buffs["range"]

        if self.time_passed >= self.next_spawn:
            damage = self.damage + self.buffs["damage"]
            shield_damage = self.shield_damage + self.buffs["damage"]
            
            if self.area_of_effect:
                if not self.aoe_buff:
                    self.update_aoe_sprite(true_range)
                    hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.enemies, False)
                    if (hits):
                        for hit in hits:
                            hit.damage(damage, shield_damage)
                            if self.slow_speed != 1:
                                hits[0].slow(self.slow_speed, self.slow_duration)
                        TOWER_DATA[self.name]["stages"][self.stage]["shoot_sound"].play()
                        self.next_spawn = pg.time.get_ticks() + self.attack_speed * 1000

            elif self.current_enemy != None:
                enemy_center = self.current_enemy.rect.center
                if (not self.current_enemy.damagable or not self.current_enemy.alive() or manhattan((enemy_center[0], enemy_center[1]), (self.rect.x, self.rect.y)) > true_range):
                    self.current_enemy = None
                else:
                    if self.rotating:
                        temp_x = enemy_center[0]
                        temp_y = enemy_center[1]

                        if (temp_y - self.rect.centery == 0):
                            if (temp_x - self.rect.centerx > 0):
                                angle = math.pi * 3 / 2
                            else:
                                angle = math.pi / 2

                        else:
                            angle = math.atan((temp_x - self.rect.centerx) / (temp_y - self.rect.centery))
                            if (temp_y - self.rect.centery > 0):
                                angle += math.pi

                        self.rotation = angle

                    rotation = self.rotation
                    increment = math.pi * 2 / self.directions
                    for i in range(self.directions):
                        if self.tracking:
                            if self.explode_on_impact:
                                TrackingExplodingProjectile([self.game, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, damage, shield_damage, self.rotation_speed, true_range, self.current_enemy, self.explosion_radius])
                            else:
                                TrackingProjectile([self.game, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, damage, shield_damage, self.rotation_speed, true_range, self.current_enemy])

                        else:
                            if self.explode_on_impact:
                                ExplodingProjectile([self.game, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, damage, shield_damage, self.rotation_speed, true_range, self.current_enemy, self.explosion_radius])
                            else:
                                Projectile([self.game, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed, self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, damage, shield_damage])

                        rotation += increment

                    self.sound.play()
                    self.next_spawn = self.attack_speed * 1000
                    self.time_passed = 0

        if not self.area_of_effect and self.current_enemy == None:
            self.search_for_enemy(true_range)
        
        if self.area_of_effect:
            if self.aoe_buff:
                hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.towers, False)
                if (hits):
                    for hit in hits:
                        hit.buff(self.aoe_buff_type, self.aoe_buff_amount)
                return # do not update passed_time for AOE Buff towers
            
        self.time_passed += self.clock.get_time()
        for buff in self.buffs:
            self.buffs[buff] = 0
            
    def update_aoe_sprite(self, true_range):
        self.aoe_sprite.rect.x = self.rect.x - (true_range - self.game.map.tilesize) / 2
        self.aoe_sprite.rect.y = self.rect.y - (true_range - self.game.map.tilesize) / 2
        self.aoe_sprite.rect.width = self.aoe_sprite.rect.height = true_range
        
    def buff(self, buff_type, amount):
        self.buffs[buff_type] = amount
            
    def upgrade(self):
        self.game.protein -= self.upgrade_cost
        self.stage += 1
        self.load_tower_data()

    def search_for_enemy(self, true_range):
        for enemy in self.game.enemies:
            if (manhattan((enemy.rect.center[0], enemy.rect.center[1]), (self.rect.center[0], self.rect.center[1])) <= true_range and (self.current_enemy == None or enemy.end_dist < self.current_enemy.end_dist)):
                self.current_enemy = enemy