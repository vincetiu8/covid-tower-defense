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
        self.size = args[4].get_size()
        self.rect = pg.Rect(args[2], args[3], self.size[0], self.size[1])
        self.rect.centerx = args[2]
        self.rect.centery = args[3]
        self.raw_image = args[4]
        self.image = self.raw_image.copy()
        self.speed = args[5]
        self.slow_speed = args[7]
        self.slow_duration = args[8]
        self.damage = args[10]
        self.direction = args[9]
        pg.transform.rotate(self.image, args[9])
        self.shield_damage = args[11]
        self.strikethrough = args[12]
        self.time_passed = 0
        self.carry = 0
        self.end = args[6] * 1000
        self.tower = args[1]

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
            self.tower.hits += 1
            if hits[0].damage(self.damage, self.shield_damage):
                self.tower.kills += 1
            if self.slow_speed != 1:
                hits[0].slow(self.slow_speed, self.slow_duration)
            if not self.strikethrough:
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
        self.explosion_radius = args[-2]
        self.explosion_color = args[-1]

    def check_for_impact(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if (hits):
            center = self.rect.center
            self.rect.width = self.rect.height = self.explosion_radius
            self.rect.center = center
            hits = pg.sprite.spritecollide(self, self.game.enemies, False)
            Explosion(self.game, self.rect.center[0], self.rect.center[1], self.explosion_radius, self.explosion_color)
            for hit in hits:
                self.tower.hits += 1
                if hit.damage(self.damage, self.shield_damage):
                    self.tower.kills += 1
                if self.slow_speed != 1:
                    hit.slow(self.slow_speed, self.slow_duration)

            if not self.strikethrough:
                self.kill()

class TrackingExplodingProjectile(TrackingProjectile, ExplodingProjectile):
    def __init__(self, args):
        TrackingProjectile.__init__(self, args[:-2])
        self.explosion_radius = args[-2]
        self.explosion_color = args[-1]

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
        self.hits = 0
        self.kills = 0

        self.buffs = []

        if not self.area_of_effect:
            self.targeting_option = 0
            self.search_for_enemy()

    def load_tower_data(self):
        data = TOWER_DATA[self.name]["stages"][self.stage]

        self.lives = data["lives"] if "lives" in data else 1
        self.range = data["range"]
        self.true_range = self.range
        self.base_image = data["base_image"]
        self.area_of_effect = data["area_of_effect"]

        self.aoe_buff = False # initialize so that we can keep track of whether a tower is an attacking or a buff one

        load_attack_attrs = True # always load unless self.area_of_effect and self.aoe_buff

        if self.area_of_effect:
            self.aoe_sprite = pg.sprite.Sprite()
            self.aoe_sprite.rect = self.rect.copy()
            self.update_aoe_sprite(self.range)
            self.aura_color = data["aura_color"]
            self.aoe_buff = data["aoe_buff"]

            if self.aoe_buff:
                aoe_buff_types = ["damage", "range"]
                self.aoe_buff_type = aoe_buff_types[data["aoe_buff_type"]] if "aoe_buff_type" != -1 else None
                self.aoe_buff_amount = data["aoe_buff_amount"]
                load_attack_attrs = False
        else:
            # Targeting options:
            # 0 - First
            # 1 - Last
            # 2 - Strong
            # 3 - Weak
            self.bullet_speed = data["bullet_speed"]
            self.bullet_lifetime = data["bullet_lifetime"]
            self.rotating = data["rotating"]
            self.tracking = data["tracking"]
            self.bullet_image = data["bullet_image"]
            self.directions = data["directions"]
            self.strikethrough = data["strikethrough"]
            if self.rotating:
                self.gun_image = data["gun_image"]
                self.rotation_speed = data["rotation_speed"] if "rotation_speed" in data else 360
                self.rotation_directions = data["rotation_directions"]if "rotation_directions" in data else 0

            self.explode_on_impact = data["explode_on_impact"]
            if self.explode_on_impact:
                self.explosion_radius = data["explosion_radius"]
                self.explosion_color = data["explosion_color"]

        if load_attack_attrs:
            self.slow_speed = data["slow_speed"]
            self.slow_duration = data["slow_duration"]
            self.damage = data["damage"]
            self.true_damage = self.damage
            self.different_shield_damage = data["different_shield_damage"]
            self.sound = data["shoot_sound"]
            self.attack_speed = data["attack_speed"]

            if self.different_shield_damage:
                self.shield_damage = data["shield_damage"]
            else:
                self.shield_damage = self.damage

            self.true_shield_damage = self.shield_damage

        if (self.stage < 2):
            data = TOWER_DATA[self.name]["stages"][self.stage + 1]
            self.upgrade_cost = data["upgrade_cost"]

    def on_remove(self):
        if self.area_of_effect and self.aoe_buff and self.aoe_buff_type is not None:
            hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.towers, False)
            if (hits):
                for hit in hits:
                    if self == hit:
                        continue
                    hit.debuff(self, self.aoe_buff_type, self.aoe_buff_amount)

    def update(self):
        if self.time_passed >= self.next_spawn:
            if self.area_of_effect:
                if self.aoe_buff:
                    hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.towers, False)
                    if (hits):
                        for hit in hits:
                            if self == hit or self in hit.buffs:
                                continue
                            hit.buff(self, self.aoe_buff_type, self.aoe_buff_amount)
                    return

                self.update_aoe_sprite(self.true_range)
                hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.enemies, False)
                if (hits):
                    for hit in hits:
                        hit.damage(self.true_damage, self.shield_damage)
                        if self.slow_speed != 1:
                            hit.slow(self.slow_speed, self.slow_duration)
                    TOWER_DATA[self.name]["stages"][self.stage]["shoot_sound"].play()
                    self.next_spawn = self.attack_speed * 1000
                    self.time_passed = 0

            elif self.current_enemy is not None:
                enemy_center = self.current_enemy.rect.center
                if not self.current_enemy.damagable or not self.current_enemy.alive() or manhattan((enemy_center[0], enemy_center[1]), (self.rect.x, self.rect.y)) > self.true_range:
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

                        if self.rotation_directions == 0:
                            self.rotation = angle

                        else:
                            increment = math.pi * 2 / self.rotation_directions
                            self.rotation = round(angle / increment) * increment


                    rotation = self.rotation
                    increment = math.pi * 2 / self.directions
                    for i in range(self.directions):
                        if self.tracking:
                            if self.explode_on_impact:
                                TrackingExplodingProjectile([self.game, self, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, self.true_damage, self.true_shield_damage, self.strikethrough, self.rotation_speed, self.true_range, self.current_enemy, self.explosion_radius, self.explosion_color])
                            else:
                                TrackingProjectile([self.game, self, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, self.true_damage, self.true_shield_damage, self.strikethrough, self.rotation_speed, self.true_range, self.current_enemy])

                        else:
                            if self.explode_on_impact:
                                ExplodingProjectile([self.game, self, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed,
                                       self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, self.true_damage, self.true_shield_damage, self.strikethrough, self.rotation_speed, self.true_range, self.current_enemy, self.explosion_radius, self.explosion_color])
                            else:
                                Projectile([self.game, self, self.rect.centerx, self.rect.centery, self.bullet_image, self.bullet_speed, self.bullet_lifetime, self.slow_speed, self.slow_duration, rotation, self.true_damage, self.true_shield_damage, self.strikethrough])

                        rotation += increment

                    self.sound.play()
                    self.next_spawn = self.attack_speed * 1000
                    self.time_passed = 0

        if not self.area_of_effect and \
                (self.current_enemy == None or
                 ((self.different_shield_damage and (not self.current_enemy.shield or self.current_enemy.shield_hp == 0))
                  or (self.slow_speed != 1 and self.current_enemy.slowed))):
            self.current_enemy = None
            self.search_for_enemy()

        self.time_passed += self.clock.get_time()

    def update_aoe_sprite(self, true_range):
        self.aoe_sprite.rect.x = self.rect.x - (true_range - self.game.map.tilesize) / 2
        self.aoe_sprite.rect.y = self.rect.y - (true_range - self.game.map.tilesize) / 2
        self.aoe_sprite.rect.width = self.aoe_sprite.rect.height = true_range

    def buff(self, buff_tower, buff_type, amount):
        self.buffs.append(buff_tower)
        if not self.aoe_buff:
            if buff_type == "range":
                self.true_range += amount
            elif buff_type == "damage":
                self.true_damage += amount
                if self.different_shield_damage:
                    self.true_shield_damage += amount

    def debuff(self, buff_tower, buff_type, amount):
        self.buffs.remove(buff_tower)
        if not self.aoe_buff:
            if buff_type == "range":
                self.true_range -= amount
            elif buff_type == "damage":
                self.true_damage -= amount
                if self.different_shield_damage:
                    self.true_shield_damage -= amount

    def upgrade(self):
        self.game.protein -= self.upgrade_cost
        self.stage += 1
        self.buffs = []
        if self.area_of_effect and self.aoe_buff and self.aoe_buff_type is not None:
            hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.towers, False)
            if (hits):
                for hit in hits:
                    if self == hit:
                        continue
                    hit.debuff(self, self.aoe_buff_type, self.aoe_buff_amount)

        self.load_tower_data()

        if self.area_of_effect and self.aoe_buff and self.aoe_buff_type is not None:
            hits = pg.sprite.spritecollide(self.aoe_sprite, self.game.towers, False)
            if (hits):
                for hit in hits:
                    if self == hit or self in hit.buffs:
                        continue
                    hit.buff(self, self.aoe_buff_type, self.aoe_buff_amount)

    def search_for_enemy(self):
        for enemy in self.game.enemies:
            if manhattan((enemy.rect.center[0], enemy.rect.center[1]), (self.rect.center[0], self.rect.center[1])) <= self.true_range and enemy.damagable:
                if self.current_enemy is None:
                    self.current_enemy = enemy
                    continue

                if (self.different_shield_damage and self.current_enemy.shield and not enemy.shield) or \
                    (self.slow_speed != 1 and enemy.slowed and not self.current_enemy.slowed):
                    continue

                elif (self.different_shield_damage and not self.current_enemy.shield and enemy.shield) or \
                    (self.slow_speed != 1 and self.current_enemy.slowed and not enemy.slowed):
                    self.current_enemy = enemy
                    continue

                if self.targeting_option == 0:
                    if enemy.end_dist < self.current_enemy.end_dist:
                        self.current_enemy = enemy

                elif self.targeting_option == 1:
                    if enemy.end_dist > self.current_enemy.end_dist:
                        self.current_enemy = enemy

                elif self.targeting_option == 2:
                    if (self.different_shield_damage and enemy.shield and enemy.shield_max_hp > self.current_enemy.shield_max_hp) or \
                            ((not self.different_shield_damage or not enemy.shield) and enemy.max_hp > self.current_enemy.max_hp):
                        self.current_enemy = enemy

                elif self.targeting_option == 3:
                    if (self.different_shield_damage and enemy.shield and enemy.shield_max_hp < self.current_enemy.shield_max_hp) or \
                            ((not self.different_shield_damage or not enemy.shield) and enemy.max_hp < self.current_enemy.max_hp):
                        self.current_enemy = enemy