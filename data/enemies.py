from data.settings import *
import random
from data.tilemap import tile_from_coords
from data.game_misc import Explosion
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, name):
        self.groups = game.enemies
        super().__init__(self.groups)
        
        self.clock = game.clock
        self.game = game
        self.name = name
        
        self.direction = [1 if random.random() < 0.5 else -1, 1 if random.random() < 0.5 else -1]
        self.carry_x = 0
        self.carry_y = 0
        self.new_node = ((tile_from_coords(x, self.game.map.tilesize), tile_from_coords(y, self.game.map.tilesize)), 0)
        self.maximising = 0
        self.damagable = True

        self.slowed = False
        self.slow_end = 0
        self.shield_end = 0
        self.total_time_passed = 0
        
        self.load_attributes(x, y)
        
        self.recreate_path()
        
    def load_attributes(self, x, y):
        # in case of mutation and the original enemy was in an artery/vein
        # scale new enemy image appopriately
        try:
            prev_scale = self.image_size / self.raw_image.get_size()[0]
        except:
            prev_scale = 1 # if it's a new enemy (not from mutation), leave image_size as is
            
        data = ENEMY_DATA[self.name]
        wave_difficulty = 1 + self.game.wave * 0.1
        game_difficulty = self.game.difficulty * 0.5 + 0.5
        self.hp = round(data["hp"] * wave_difficulty * game_difficulty)
        self.max_hp = self.hp
        self.speed = data["speed"]
        self.dropped_protein = data["protein"]
        self.original_image = data["image"]
        self.raw_image = self.original_image
        self.flying = data["flying"]
        self.shield = data["shield"]
        if self.shield:
            self.shield_max_hp = round(data["shield_hp"] * wave_difficulty * game_difficulty)
            self.shield_hp = self.shield_max_hp
            self.shield_max_recharge_delay = data["shield_recharge_delay"]
            self.shield_recharge_rate = data["shield_recharge_rate"]

        self.explode_on_death = data["explode_on_death"]
        if self.explode_on_death:
            self.explode_radius = data["explode_radius"]
        
        self.mutate = data["mutate"]
        if self.mutate:
            self.mutation_type = data["mutation_type"]
            self.mutation_time = data["mutation_time"]
        
        self.image_size = int(self.raw_image.get_size()[0] * prev_scale)
        self.image = pg.transform.scale(self.raw_image, (self.image_size, self.image_size))
        image_size = self.raw_image.get_size()
        self.rect = pg.Rect(x, y, image_size[0], image_size[1])

    def update(self):
        passed_time = self.clock.get_time() / 1000
        self.slow_end -= passed_time
        self.total_time_passed += passed_time

        if self.shield and self.shield_hp != self.shield_max_hp:
            if self.shield_recharge_delay <= 0:
                self.shield_hp += 1
                self.shield_recharge_delay = self.shield_recharge_rate

            else:
                self.shield_recharge_delay -= passed_time

        if self.slowed and self.slow_end <= 0:
            self.reset_speed()
            
        if self.mutate:
            if self.total_time_passed >= self.mutation_time:
                self.name = list(ENEMY_DATA)[self.mutation_type]
                self.load_attributes(self.rect.x, self.rect.y)

        if (self.maximising < 0 and self.image.get_width() > 0 or self.maximising > 0 and self.image.get_width() < self.rect.w):
            self.image_size = max(0, min(self.image_size + self.maximising, self.rect.w))
            if self.image_size > 0:
                if self.image_size == self.rect.w:
                    self.maximising = 0
                self.image = pg.transform.scale(self.raw_image, (self.image_size, self.image_size))
            else:
                self.maximising = 0

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
            
    def damage(self, dam, shield_dam):
        if self.shield and self.shield_hp > 0:
            self.shield_recharge_delay = self.shield_max_recharge_delay
            if shield_dam > self.shield_hp:
                self.shield_hp = 0
            else:
                self.shield_hp -= shield_dam

        else:
            self.hp -= dam

        if (self.hp <= 0):
            ENEMY_DEATH_SOUND.play()
            self.game.protein += self.dropped_protein
            self.game.ui.generate_header()
            self.game.ui.generate_body_wrapper()
            if self.explode_on_death:
                EnemyExplosion(self.game, self.rect.center[0], self.rect.center[1], self.explode_radius)
            self.kill()
            return True
        return False

    def get_hp_surf(self):
        if self.hp < 0:
            return None

        hp_surf = pg.Surface((math.ceil(math.log10(self.hp) * 10), 5))
        if self.is_slowed():
            hp_surf.fill(RED)
        else:
            hp_surf.fill(GREEN)

        if not self.shield or self.shield_hp == 0:
            return hp_surf
        
        if self.shield_hp == 0:
            return hp_surf

        shield_surf = pg.Surface((math.ceil(math.log10(self.shield_hp) * 10), 5))
        shield_surf.fill(CYAN)
        combo_surf = pg.Surface((max(shield_surf.get_width(), hp_surf.get_width()), 10)).convert_alpha()
        combo_surf.fill((0, 0, 0, 0))
        combo_surf.blit(hp_surf, hp_surf.get_rect(center=(combo_surf.get_rect().center[0], 7)))
        combo_surf.blit(shield_surf, shield_surf.get_rect(center=(combo_surf.get_rect().center[0], 2)))
        return combo_surf

    def recreate_path(self):
        self.path = self.game.pathfinder.astar((self.new_node[0], self.new_node[1]), self.game.goals, self.flying)
        if not self.path and not self.flying:
            self.path = self.game.pathfinder.astar((self.new_node[0], self.new_node[1]), self.game.goals, True)
        self.load_next_node()

    def load_next_node(self):
        if self.path == False:
            print("PATHFINDING ERROR") # This should never happen
            self.kill()
            return

        if (len(self.path) == 0):
            self.game.lives = max(self.game.lives - 1, 0)
            self.game.ui.generate_header_wrapper()
            self.game.protein += self.dropped_protein   # TODO: Remove this dev feature
                                                        # (enemies shouldn't drop protein if they reach the goal)
            
            if self.game.lives <= 0:
                self.game.cause_of_death = " ".join(self.name.split("_")).title() # removes underscores, capitalizes it properly

            self.kill()
            return
        
        self.end_dist = len(self.path)
        prevlayer = self.new_node[1]
        self.new_node = self.path.pop(0)
        
        if abs(prevlayer) == 1 and abs(self.new_node[1]) == 2:
            self.maximising = -4
            self.damagable = False
        elif abs(prevlayer) == 2 and abs(self.new_node[1]) == 1:
            self.maximising = 4
            self.damagable = False
        elif prevlayer == 0:
            self.damagable = True

        self.new_node_rect = pg.Rect(self.new_node[0][0] * self.game.map.tilesize, self.new_node[0][1] * self.game.map.tilesize, self.game.map.tilesize, self.game.map.tilesize)
        
    def reset_speed(self):
        self.speed = ENEMY_DATA[self.name]["speed"]
        self.raw_image = self.original_image
        self.image = pg.transform.scale(self.raw_image, (self.image_size, self.image_size))
        self.slowed = False

    def is_slowed(self):
        return self.slowed

    def slow(self, slow_speed, slow_duration):
        self.speed = ENEMY_DATA[self.name]["speed"]
        self.slowed = True
        self.slow_end = self.clock.get_time() / 1000 + slow_duration
        self.speed *= slow_speed

        image_surf = pg.Surface(self.image.get_size()).convert_alpha()
        image_surf.fill((0, 0, 0, 0))
        image_surf.blit(self.original_image.convert_alpha(), (0, 0))
        image_surf.fill(HALF_GREEN, None, pg.BLEND_RGBA_MULT)
        self.raw_image = image_surf
        self.image = pg.transform.scale(self.raw_image, (self.image_size, self.image_size))

class EnemyExplosion(Explosion):
    def __init__(self, game, x, y, rad):
        hit = False
        
        for tile_x in range(tile_from_coords(x - rad / 2, game.map.tilesize), tile_from_coords(x + rad / 2, game.map.tilesize) + 1):
            for tile_y in range(tile_from_coords(y - rad / 2, game.map.tilesize), tile_from_coords(y + rad / 2, game.map.tilesize) + 1):
                tower = game.map.get_tower(tile_x, tile_y)
                if tower != None:
                    hit = True
                    game.map.remove_tower(tile_x, tile_y)
                    tower.on_remove()
                    tower.kill()
        
        if hit:
            game.pathfinder.clear_nodes(game.map.get_map())
            game.draw_tower_bases_wrapper()
            game.make_stripped_path_wrapper()
            for enemy in game.enemies:
                enemy.recreate_path()
        super().__init__(game, x, y, rad)
