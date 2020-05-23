import pygame as pg
from data.main import Game
from data.tilemap import *
from data.pathfinding import *
from data.game import *
from data.settings import TOWER_DATA
import data.settings as settings

import json
import textwrap
from os import path
from copy import deepcopy

class DevClass(Game):
    def __init__(self, clock):
        self.clock = clock
        self.tower_names = SAVE_DATA["owned_towers"]
        self.enemy_names = list(ENEMY_DATA.keys())

    def reload_level(self, map):
        self.map = TiledMap(path.join(MAP_FOLDER, "{}.tmx".format(map)))
        super().load_data()

    def new(self):
        self.current_tower = 0
        self.current_stage = 0
        self.current_enemy = 0

        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.explosions = pg.sprite.Group()

        self.protein = 0
        self.lives = 0
        self.start_data = []

        self.map.clear_map()

        for tile_object in self.map.tmxdata.objects:
            if "start" in tile_object.name:
                self.start_data.insert(int(tile_object.name[5:]),
                                       pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height))
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        self.map.set_valid_tower_tile(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                      tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                      0)  # make start tile a wall so you can't place a tower on it
                        # this does not affect the path finding algo
            if tile_object.name == "goal":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        Goal(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "tower":
                self.map.add_tower(tile_from_xcoords(tile_object.x, self.map.tilesize),
                                   tile_from_xcoords(tile_object.y, self.map.tilesize),
                                   Tower(self, tile_object.x, tile_object.y, self.tower_names[self.current_tower]))

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        base_map = deepcopy(self.map.get_map())
        tower_map = self.map.get_tower_map()
        for i, row in enumerate(base_map):
            for j, cell in enumerate(row):
                if tower_map[i][j] != None:
                    base_map[i][j] = 0
        self.pathfinder = Pathfinder(base_map = base_map)
        self.pathfinder.clear_nodes(self.map.get_map())
        self.draw_tower_bases_wrapper()

    def get_attr_surf(self):
        self.attr_surf = self.ui.get_ui()

    def draw_tower_bases_wrapper(self):
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def make_stripped_path_wrapper(self):
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))

    def load_ui(self, save=False):
        self.ui = DevUI(save)
        self.ui.new_attr(Attribute("tower_name", {
            "type": "select",
            "values": self.tower_names
        }, self.current_tower, disabled=False, reload_on_change=True))
        self.ui.new_attr(Attribute("tower_stage", {
            "type": "float",
            "min": 0,
            "max": 2,
            "dp": 0,
            "increment": 1
        }, self.current_stage, disabled=False, reload_on_change=True))

    def reload_towers(self):
        for x, list in enumerate(self.map.get_tower_map()):
            for y, tower in enumerate(list):
                if tower != None:
                    self.map.remove_tower(x, y)
                    temp_tower = Tower(self, tower.rect.x, tower.rect.y, self.tower_names[self.current_tower])
                    temp_tower.stage = self.current_stage
                    temp_tower.load_tower_data()
                    self.map.add_tower(x, y, temp_tower)
        for enemy in self.enemies:
            enemy.recreate_path()
        self.pathfinder.clear_nodes(self.map.get_map())
        self.draw_tower_bases_wrapper()
        self.make_stripped_path_wrapper()

    def reload_enemies(self):
        for enemy in self.enemies:
            enemy.kill()
        self.enemies = pg.sprite.Group() 
        for start in self.starts:
            start.enable_spawning()
            start.enemy_type = self.enemy_names[self.current_enemy]
        self.make_stripped_path_wrapper()

    def update(self):
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()
        self.explosions.update()

    def draw(self):
        surface = pg.Surface((self.map.width, self.map.height))
        surface.fill((0, 0, 0))
        
        surface.blit(self.map_img, self.map_rect)
        surface.blit(self.map_objects, self.map_rect)

        surface.blit(self.path_surf, self.path_surf.get_rect())
        surface.blit(self.tower_bases_surf,
                     self.tower_bases_surf.get_rect())

        for tower in self.towers:
            if tower.area_of_effect or not tower.rotating:
                continue
            rotated_image = pg.transform.rotate(tower.gun_image, math.degrees(tower.rotation))
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            surface.blit(rotated_image, new_rect)

        total_hp_surf = pg.Surface((self.map.width, self.map.height)).convert_alpha()
        total_hp_surf.fill((0, 0, 0, 0))
        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)
            hp_surf = enemy.get_hp_surf()
            if hp_surf != None:
                total_hp_surf.blit(hp_surf, hp_surf.get_rect(center=(enemy.rect.center[0], enemy.rect.center[1] - enemy.image_size // 2 - 10)))
        surface.blit(total_hp_surf, (0, 0))

        for projectile in self.projectiles:
            surface.blit(projectile.image, projectile.rect)

        surface.blit(self.aoe_surf, (0, 0))

        for explosion in self.explosions:
            surface.blit(explosion.get_surf(), (explosion.x, explosion.y))

        surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.blit(self.camera.apply_image((surface)), (0, 0))

        ui_pos = (SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)
        if self.ui.active:
            ui = self.attr_surf
            ui_rect = ui.get_rect(topright=ui_pos)
            surf.blit(ui, ui_rect)
            surf.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright=ui_rect.topleft))
        else:
            surf.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright=ui_pos))
        
        return surf

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui.active and RIGHT_ARROW_IMG.get_rect(topright = self.attr_surf.get_rect(topright = (SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)).topleft).collidepoint(event.pos):
                self.ui.active = False
                return -1
            elif not self.ui.active and LEFT_ARROW_IMG.get_rect(topright=(SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)).collidepoint(event.pos):
                self.ui.active = True
                return -1

        result = self.ui.event(event, SCREEN_WIDTH - self.attr_surf.get_width())
        if result == -1:
            return -1

        elif isinstance(result, str):
            if result == "reload_towers":
                self.reload_towers()
                return -1
            elif result == "reload_enemies":
                self.reload_enemies()
                return -1
            return result

        return -2

class TowerPreviewMenu(DevClass):
    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().reload_level("tower_test")
        super().load_data()
        super().new()
        self.starts = [Start(self, start, self.enemy_names[self.current_enemy], -1, 0, 5) for start in
                       range(len(self.start_data))]
        self.make_stripped_path_wrapper()
        self.new_tower_name = ""
        self.load_ui()

    def load_ui(self):
        super().load_ui()
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy, disabled=False))
        for attr in ATTR_DATA["tower"]:
            self.ui.new_attr(
                Attribute(attr, ATTR_DATA["tower"][attr], TOWER_DATA[self.tower_names[self.current_tower]][attr]))

        ignore = []
        for attr in ATTR_DATA["stage"]:
            if attr in ignore:
                continue
            if ATTR_DATA["stage"][attr]["type"] == "bool" and "ignore_if_true" in ATTR_DATA["stage"][
                attr] or "ignore_if_false" in ATTR_DATA["stage"][attr]:
                if "ignore_if_true" in ATTR_DATA["stage"][attr] and \
                        TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr]:
                    ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_true"])
                elif "ignore_if_false" in ATTR_DATA["stage"][attr] and not \
                TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr]:
                    ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_false"])
            self.ui.new_attr(Attribute(attr, ATTR_DATA["stage"][attr],
                                       TOWER_DATA[self.tower_names[self.current_tower]]["stages"][
                                           self.current_stage][attr]))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        reload = False
        self.current_enemy = attrs.pop("enemy_name")
        for attr in attrs:
            if attr == "scroll_position":
                continue
            elif attr == "tower_name":
                if self.current_tower != attrs[attr]:
                    reload = True
                continue
            elif attr == "tower_stage":
                if self.current_stage != attrs[attr]:
                    reload = True
                continue
        if reload:
            self.current_tower = attrs["tower_name"]
            self.current_stage = attrs["tower_stage"]
            self.load_ui()  # has to be called so UI reloads when changing tower_name while editing a description

        else:
            self.reload_towers()
            self.reload_enemies()
            self.get_attr_surf()

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            if result == "menu":
                return result
            elif result == "scroll_position":
                self.get_attr_surf()
            elif result == "new_tower_name":
                self.create_new_tower()
                self.load_ui()
            else:
                self.reload_attrs()
                self.load_ui()

        elif result == -2:
            self.reload_attrs()

        return -1

class TowerEditMenu(TowerPreviewMenu):
    def new(self, args):
        self.tower_names = list(TOWER_DATA.keys())
        # initialize all variables and do all the setup for a new game
        super().new(args)

    def load_ui(self):
        DevClass.load_ui(self, True)
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy, disabled=False))
        self.ui.new_attr(Attribute("new_tower_name", {"type": "string"}, "", disabled=False))
        
        for attr in ATTR_DATA["tower"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["tower"][attr], TOWER_DATA[self.tower_names[self.current_tower]][attr], disabled=False))

        ignore = []
        for attr in ATTR_DATA["stage"]:
            if attr in ignore:
                continue
            if ATTR_DATA["stage"][attr]["type"] == "bool" and "ignore_if_true" in ATTR_DATA["stage"][attr] or "ignore_if_false" in ATTR_DATA["stage"][attr]:
                self.ui.new_attr(Attribute(attr, ATTR_DATA["stage"][attr],
                                           TOWER_DATA[self.tower_names[self.current_tower]]["stages"][
                                               self.current_stage][attr], disabled=False, reload_on_change=True))
                if "ignore_if_true" in ATTR_DATA["stage"][attr] and TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr]:
                    ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_true"])
                elif "ignore_if_false" in ATTR_DATA["stage"][attr] and not TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr]:
                    ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_false"])
            else:
                try:
                    self.ui.new_attr(Attribute(attr, ATTR_DATA["stage"][attr],
                                               TOWER_DATA[self.tower_names[self.current_tower]]["stages"][
                                                   self.current_stage][attr], disabled=False))
                except:
                    self.ui.new_attr(Attribute(attr, ATTR_DATA["stage"][attr], ATTR_DATA["stage"][attr]["default"], disabled=False))
                    TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr] = ATTR_DATA["stage"][attr]["default"]

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        reload = False
        self.current_enemy = attrs.pop("enemy_name")
        self.new_tower_name = attrs.pop("new_tower_name")
        for attr in attrs:
            if attr == "scroll_position":
                continue
            elif attr == "tower_name":
                if self.current_tower != attrs[attr]:
                    reload = True
                continue
            elif attr == "tower_stage":
                if self.current_stage != attrs[attr]:
                    reload = True
                continue
            elif attr in ATTR_DATA["tower"]:
                TOWER_DATA[self.tower_names[self.current_tower]][attr] = attrs[attr]
                continue
            else:
                if ATTR_DATA["stage"][attr]["type"] == "bool" and ((attrs[attr] and not TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr] and "ignore_if_false" in ATTR_DATA["stage"][attr]) or (not attrs[attr] and TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr] and "ignore_if_true" in ATTR_DATA["stage"][attr])):
                    reload = True
                TOWER_DATA[self.tower_names[self.current_tower]]["stages"][self.current_stage][attr] = attrs[attr]
        if reload:
            self.current_tower = attrs["tower_name"]
            self.current_stage = attrs["tower_stage"]
            self.load_ui() # has to be called so UI reloads when changing tower_name while editing a description

        else:
            self.reload_towers()
            self.reload_enemies()
            self.get_attr_surf()

    def event(self, event):
        return super().event(event)

    def create_new_tower(self):
        TOWER_DATA[self.new_tower_name] = {}
        for attr in ATTR_DATA["tower"]:
            TOWER_DATA[self.new_tower_name][attr] = ATTR_DATA["tower"][attr]["default"]
            
        TOWER_DATA[self.new_tower_name]["stages"] = []
            
        for stage in range(3):
            TOWER_DATA[self.new_tower_name]["stages"].append({})
            for attr in ATTR_DATA["stage"]:
                TOWER_DATA[self.new_tower_name]["stages"][stage][attr] = ATTR_DATA["stage"][attr]["default"]
            
            TOWER_DATA[self.new_tower_name]["stages"][stage]["gun_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_gun" + str(stage) + ".png"))
            TOWER_DATA[self.new_tower_name]["stages"][stage]["base_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_base" + str(stage) + ".png"))
            TOWER_DATA[self.new_tower_name]["stages"][stage]["bullet_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_bullet" + str(stage) + ".png"))
            TOWER_DATA[self.new_tower_name]["stages"][stage]["shoot_sound"] = pg.mixer.Sound(path.join(TOWERS_AUD_FOLDER, "{}.wav".format(self.new_tower_name)))
            temp_base = TOWER_DATA[self.new_tower_name]["stages"][stage]["base_image"].copy()
            temp_base.blit(TOWER_DATA[self.new_tower_name]["stages"][stage]["gun_image"],
                           TOWER_DATA[self.new_tower_name]["stages"][stage]["gun_image"].get_rect(
                               center=TOWER_DATA[self.new_tower_name]["stages"][stage]["base_image"].get_rect().center))
            TOWER_DATA[self.new_tower_name]["stages"][stage]["image"] = temp_base
        self.tower_names = list(TOWER_DATA.keys())
        self.current_tower = self.tower_names.index(self.new_tower_name)
        self.current_stage = 0

class EnemyPreviewMenu(DevClass):
    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().reload_level("enemy_test")
        super().load_data()
        super().new()
        self.starts = [Start(self, start, self.enemy_names[self.current_enemy], -1, 0, 2) for start in range(len(self.start_data))]
        self.make_stripped_path_wrapper()
        self.new_enemy_name = ""
        self.load_ui()

    def load_ui(self):
        super().load_ui()
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy, disabled=False, reload_on_change=True))

        ignore = []
        for attr in ATTR_DATA["enemy"]:
            if attr in ignore:
                continue
            if ATTR_DATA["enemy"][attr]["type"] == "bool" and "ignore_if_true" in ATTR_DATA["enemy"][
                attr] or "ignore_if_false" in ATTR_DATA["enemy"][attr]:
                if "ignore_if_true" in ATTR_DATA["enemy"][attr] and \
                        ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]:
                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_true"])
                elif "ignore_if_false" in ATTR_DATA["enemy"][attr] and not \
                ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]:
                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_false"])
            self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr],
                                               ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_attrs(self):
        reload = False
        attrs = self.ui.get_attrs()
        self.current_tower = attrs.pop("tower_name")
        self.current_stage = attrs.pop("tower_stage")
        for attr in attrs:
            if attr == "scroll_position":
               continue
            elif attr == "enemy_name":
                if self.current_enemy != attrs[attr]:
                    reload = True
                continue
            else:
                if ATTR_DATA["enemy"][attr]["type"] == "bool" and ((attrs[attr] and not ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] and "ignore_if_false" in ATTR_DATA["enemy"][attr]) or (not attrs[attr] and ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] and "ignore_if_true" in ATTR_DATA["enemy"][attr])):
                    reload = True
                ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] = attrs[attr]

        if reload:
            self.current_enemy = attrs["enemy_name"]
            self.load_ui() # has to be called so UI reloads when changing tower_name while editing a description

        else:
            self.reload_towers()
            self.reload_enemies()
            self.get_attr_surf()

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            if result == "menu":
                return result
            elif result == "scroll_position":
                self.get_attr_surf()
            elif result == "new_enemy_name":
                self.create_new_enemy()
                self.load_ui()
            else:
                self.reload_attrs()
                self.load_ui()

        elif result == -2:
            self.reload_attrs()

        return -1

class EnemyEditMenu(EnemyPreviewMenu):
    def new(self, args):
        self.tower_names = list(TOWER_DATA.keys())
        super().new(args)

    def load_ui(self):
        DevClass.load_ui(self, True)
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy, disabled=False, reload_on_change=True))
        self.ui.new_attr(Attribute("new_enemy_name", {"type": "string"}, "", disabled=False))

        ignore = []
        for attr in ATTR_DATA["enemy"]:
            if attr in ignore:
                continue
            if ATTR_DATA["enemy"][attr]["type"] == "bool" and "ignore_if_true" in ATTR_DATA["enemy"][
                attr] or "ignore_if_false" in ATTR_DATA["enemy"][attr]:
                self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr],
                                           ENEMY_DATA[self.enemy_names[self.current_enemy]][attr], disabled=False, reload_on_change=True))
                if "ignore_if_true" in ATTR_DATA["enemy"][attr] and \
                        ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]:
                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_true"])
                elif "ignore_if_false" in ATTR_DATA["enemy"][attr] and not \
                ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]:
                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_false"])
            else:
                try:
                    self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr],
                                               ENEMY_DATA[self.enemy_names[self.current_enemy]][attr], disabled=False))
                except:
                    self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr], ATTR_DATA["enemy"][attr]["default"], disabled=False))
                    ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] = ATTR_DATA["enemy"][attr]["default"]

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_attrs(self):
        reload = False
        attrs = self.ui.get_attrs()
        self.current_tower = attrs.pop("tower_name")
        self.current_stage = attrs.pop("tower_stage")
        self.new_enemy_name = attrs.pop("new_enemy_name")
        for attr in attrs:
            if attr == "scroll_position":
               continue
            elif attr == "enemy_name":
                if self.current_enemy != attrs[attr]:
                    reload = True
                continue
            else:
                if ATTR_DATA["enemy"][attr]["type"] == "bool" and ((attrs[attr] and not ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] and "ignore_if_false" in ATTR_DATA["enemy"][attr]) or (not attrs[attr] and ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] and "ignore_if_true" in ATTR_DATA["enemy"][attr])):
                    reload = True
                ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] = attrs[attr]

        if reload:
            self.current_enemy = attrs["enemy_name"]
            self.load_ui() # has to be called so UI reloads when changing tower_name while editing a description

        else:
            self.reload_towers()
            self.reload_enemies()
            self.get_attr_surf()

    def event(self, event):
        return super().event(event)

    def create_new_enemy(self):
        ENEMY_DATA[self.new_enemy_name] = {}
        for attr in ATTR_DATA["enemy"]:
            ENEMY_DATA[self.new_enemy_name][attr] = ATTR_DATA["enemy"][attr]["default"]
        ENEMY_DATA[self.new_enemy_name]["image"] = pg.image.load(path.join(ENEMIES_IMG_FOLDER, "{}.png".format(self.new_enemy_name)))
        ENEMY_DATA[self.new_enemy_name]["death_sound"] = pg.mixer.Sound(path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(enemy)))
        self.enemy_names = list(ENEMY_DATA.keys())
        self.current_enemy = self.enemy_names.index(self.new_enemy_name)

class LevelEditMenu(DevClass):
    def __init__(self, clock):
        super().__init__(clock)
        self.level = 0
        self.wave = 0
        self.sub_wave = 0
        self.enemy_types = list(ENEMY_DATA.keys())

    def reload_level(self):
        super().reload_level("map{}".format(self.level))
        super().load_data()
        super().new()
        self.reload_enemies()
        self.make_stripped_path_wrapper()

    def new(self, args):
        self.tower_names = list(TOWER_DATA.keys())
        # initialize all variables and do all the setup for a new game
        self.reload_level()
        self.load_ui()

    def load_ui(self):
        DevClass.load_ui(self, True)

        self.ui.new_attr(Attribute("level",
                                   {"type": "float",
                                    "min": 0,
                                    "max": len(LEVEL_DATA),
                                    "increment": 1,
                                    "dp": 0
                                    }, self.level, disabled=False))
        for attr in ATTR_DATA["level"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["level"][attr],
                                       LEVEL_DATA[self.level][attr], disabled=False))

        self.ui.new_attr(Attribute("wave",
                                   {"type": "float",
                                    "min": 0,
                                    "max": len(LEVEL_DATA[self.level]["waves"]),
                                    "increment": 1,
                                    "dp": 0
                                    }, self.wave, disabled=False))
        self.ui.new_attr(Attribute("sub_wave",
                                    {"type": "float",
                                     "min": 0,
                                     "max": len(LEVEL_DATA[self.level]["waves"][self.wave]),
                                     "increment": 1,
                                     "dp": 0
                                     }, self.sub_wave, disabled=False))

        for attr in ATTR_DATA["sub_wave"]:
            temp_dat = ATTR_DATA["sub_wave"][attr].copy()
            temp_val = LEVEL_DATA[self.level]["waves"][self.wave][self.sub_wave][attr]
            if attr == "start":
                temp_dat["max"] = len(self.start_data) - 1
            elif attr == "enemy_type":
                temp_dat["values"] = self.enemy_types
                temp_val = self.enemy_types.index(temp_val)
            self.ui.new_attr(Attribute(attr, temp_dat, temp_val, disabled=False))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_enemies(self):
        for enemy in self.enemies:
            enemy.kill()

        self.starts = []
        self.enemies = pg.sprite.Group()
        for s in LEVEL_DATA[self.level]["waves"][self.wave]:
            self.starts.append(Start(self, s["start"], s["enemy_type"], s["enemy_count"], s["spawn_delay"], s["spawn_rate"]))
            self.starts[-1].enable_spawning()

    def update(self):
        super().update()
        if self.current_wave_done() and len(self.enemies) == 0:
            self.reload_enemies()

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        load = False
        create_level = False
        create_wave = False
        create_sub_wave = False
        for attr in attrs:
            if attr == "level":
                if self.level != attrs[attr]:
                    if attrs[attr] == len(LEVEL_DATA):
                        create_level = True
                    attrs["wave"] = 0
                    attrs["sub_wave"] = 0
                    load = True
            elif attr == "wave":
                if self.wave != attrs[attr]:
                    if attrs[attr] == len(LEVEL_DATA[self.level]["waves"]):
                        create_wave = True
                    attrs["sub_wave"] = 0
                    load = True
            elif attr == "sub_wave":
                if self.sub_wave != attrs[attr]:
                    if attrs[attr] == len(LEVEL_DATA[self.level]["waves"][self.wave]):
                        create_sub_wave = True
                    load = True
            elif attr in ATTR_DATA["level"]:
                LEVEL_DATA[self.level][attr] = attrs[attr]
            else:
                if attr == "enemy_type":
                    attrs[attr] = self.enemy_types[attrs[attr]]
                LEVEL_DATA[self.level]["waves"][self.wave][self.sub_wave][attr] = attrs[attr]
        if create_level:
            self.level = attrs["level"]
            self.create_new_level()
            self.load_ui()

        elif create_wave:
            self.wave = attrs["wave"]
            self.create_new_wave()
            self.load_ui()

        elif create_sub_wave:
            self.sub_wave = attrs["sub_wave"]
            self.create_new_sub_wave()
            self.load_ui()

        elif load:
            self.level = attrs["level"]
            self.wave = attrs["wave"]
            self.sub_wave = attrs["sub_wave"]
            self.reload_level()
            self.load_ui()

        else:
            self.reload_towers()
            self.reload_enemies()
            self.get_attr_surf()

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            if result == "menu":
                return result
            elif result == "scroll_position":
                self.get_attr_surf()
            elif result == "new_tower_name":
                self.create_new_tower()
                self.load_ui()
            else:
                self.reload_attrs()
                self.load_ui()

        elif result == -2:
            self.reload_attrs()

        return -1

    def create_new_level(self):
        LEVEL_DATA.append({})
        self.wave = 0
        for attr in ATTR_DATA["level"]:
            LEVEL_DATA[self.level][attr] = ATTR_DATA["level"][attr]["default"]
        LEVEL_DATA[self.level]["waves"] = []
        self.create_new_wave()
        self.reload_level()

    def create_new_wave(self):
        LEVEL_DATA[self.level]["waves"].append([])
        self.sub_wave = 0
        self.create_new_sub_wave()

    def create_new_sub_wave(self):
        LEVEL_DATA[self.level]["waves"][self.wave].append({})
        for attr in ATTR_DATA["sub_wave"]:
            if attr == "enemy_type":
                LEVEL_DATA[self.level]["waves"][self.wave][self.sub_wave][attr] = self.enemy_types[ATTR_DATA["sub_wave"][attr]["default"]]
            else:
                LEVEL_DATA[self.level]["waves"][self.wave][self.sub_wave][attr] = ATTR_DATA["sub_wave"][attr]["default"]
class DevUI():
    def __init__(self, save=False):
        self.save = save
        self.save_text = "Save Settings"
        self.revert_save_text_event = pg.event.Event(pg.USEREVENT + 1)
        self.attributes = []
        self.active = True
        self.max_attrs = 0
        self.attributes.insert(0, Attribute("scroll_position", {
            "type": "float",
            "min": 1,
            "max": 1,
            "increment": 1,
            "dp": 0
        }, 1, disabled=False))

    def new_attr(self, attribute):
        self.attributes.append(attribute)

    def get_attrs(self):
        values = {}
        for attr in self.attributes:
            values[attr.name] = attr.current_value
        return values

    def get_ui(self):
        surf_list = []
        height = MENU_OFFSET
        width_1 = MENU_OFFSET
        width_2 = MENU_OFFSET
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.2))
        
        if self.save:
            save_text = font.render(self.save_text, 1, WHITE)
            save_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
            round(save_text.get_rect().width * 1.5), save_text.get_height())).copy().convert_alpha()
            save_button.blit(save_text, save_text.get_rect(center=save_button.get_rect().center))
            self.save_button_rect = save_button.get_rect()
            self.save_button_rect.x = MENU_OFFSET
            width_1 += self.save_button_rect.width + MENU_OFFSET

        done_text = font.render("Done", 1, WHITE)
        done_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(done_text.get_rect().width * 1.5), done_text.get_height())).copy().convert_alpha()
        done_button.blit(done_text, done_text.get_rect(center=done_button.get_rect().center))
        self.done_button_rect = done_button.get_rect()

        if self.save:
            self.done_button_rect.x = self.save_button_rect.width + MENU_OFFSET * 2
        else:
            self.done_button_rect.x = MENU_OFFSET
        width_1 += self.done_button_rect.width + MENU_OFFSET
        height += self.done_button_rect.height + MENU_OFFSET

        if self.save:
            temp_surf = pg.Surface((width_1, self.done_button_rect.height))
            temp_surf.fill(DARK_GREY)
            t_width = MENU_OFFSET
            for save_surf in [save_button, done_button]:
                temp_surf.blit(save_surf, (t_width, 0))
                t_width += save_surf.get_rect().width + MENU_OFFSET
            surf_list.append(temp_surf)

        else:
            surf_list.append(done_button)

        reload_tower_text = font.render("Reload Towers", 1, WHITE)
        reload_tower_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
            round(reload_tower_text.get_rect().width * 1.5), reload_tower_text.get_height())).copy().convert_alpha()
        reload_tower_button.blit(reload_tower_text, reload_tower_text.get_rect(center=reload_tower_button.get_rect().center))
        self.reload_tower_button_rect = reload_tower_button.get_rect()
        self.reload_tower_button_rect.x = MENU_OFFSET
        width_2 += self.reload_tower_button_rect.width + MENU_OFFSET
        height += reload_tower_button.get_rect().height + MENU_OFFSET

        reload_enemy_text = font.render("Reload Enemies", 1, WHITE)
        reload_enemy_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
            round(reload_enemy_text.get_rect().width * 1.5), reload_enemy_text.get_height())).copy().convert_alpha()
        reload_enemy_button.blit(reload_enemy_text, reload_enemy_text.get_rect(center=reload_enemy_button.get_rect().center))
        self.reload_enemy_button_rect = reload_enemy_button.get_rect()
        self.reload_enemy_button_rect.x = self.reload_tower_button_rect.width + MENU_OFFSET * 2
        width_2 += self.reload_enemy_button_rect.width + MENU_OFFSET
        

        temp_surf = pg.Surface((width_2, self.reload_tower_button_rect.height))
        temp_surf.fill(DARK_GREY)
        t_width = MENU_OFFSET
        for reload_surf in [reload_tower_button, reload_enemy_button]:
            temp_surf.blit(reload_surf, (t_width, 0))
            t_width += reload_surf.get_rect().width + MENU_OFFSET
        surf_list.insert(0, temp_surf)
        
        width = max(width_1, width_2)

        attr0_surf = self.attributes[0].draw()
        self.attributes[0].fix_offset(0, MENU_OFFSET)
        height += attr0_surf.get_height() + MENU_OFFSET
        surf_list.insert(0, attr0_surf)

        if self.max_attrs == 0:
            for attr in self.attributes[1:]:
                attr_surf = attr.draw()
                attr.fix_offset(0, height - self.done_button_rect.height - MENU_OFFSET)
                
                width = max(width, attr_surf.get_width())
                height += attr_surf.get_height() + MENU_OFFSET
                if height >= SCREEN_HEIGHT - MENU_OFFSET:
                    height -= attr_surf.get_height() + MENU_OFFSET
                    break
                
                self.max_attrs += 1
                surf_list.insert(-1, attr_surf)
                
            self.attributes[0].max = len(self.attributes) - self.max_attrs

        else:
            for attr in self.attributes[self.attributes[0].current_value:self.attributes[0].current_value + self.max_attrs]:
                attr_surf = attr.draw()
                attr.fix_offset(0, height - self.done_button_rect.height - MENU_OFFSET)
                
                width = max(width, attr_surf.get_width())
                height += attr_surf.get_height() + MENU_OFFSET
                
                surf_list.insert(-1, attr_surf)

        surf = pg.Surface((width + MENU_OFFSET, height))
        surf.fill(DARK_GREY)
        height = MENU_OFFSET
        for attr in surf_list:
            surf.blit(attr, (MENU_OFFSET, height))
            height += attr.get_height() + MENU_OFFSET

        self.done_button_rect.y = height - MENU_OFFSET - self.done_button_rect.height

        if self.save:
            self.save_button_rect.y = self.done_button_rect.y

        self.reload_enemy_button_rect.y = self.reload_tower_button_rect.y = MENU_OFFSET * 2 + attr0_surf.get_height()

        return surf

    def event(self, event, w):
        return_val = -1
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                offset = (event.pos[0] - w, event.pos[1] - MENU_OFFSET)
                if self.save and self.save_button_rect.collidepoint(offset):
                    for i, level in enumerate(LEVEL_DATA):
                        if "enemies" in level:
                            level.pop("enemies")
                        with open(path.join(LEVELS_FOLDER, "level{}.json".format(i)), 'w') as out_file:
                            json.dump(level, out_file, indent=4)
                    for level in LEVEL_DATA:
                        enemies = []
                        for wave in level["waves"]:
                            for sub_wave in wave:
                                enemy = sub_wave["enemy_type"]
                                if enemy not in enemies:
                                    enemies.append(enemy)
                        level["enemies"] = enemies
                    for enemy in ENEMY_DATA:
                        if "image" in ENEMY_DATA[enemy]:
                            ENEMY_DATA[enemy].pop("image")
                        if "death_sound" in ENEMY_DATA[enemy]:
                            ENEMY_DATA[enemy].pop("death_sound")
                        ignore = []
                        for attr in ATTR_DATA["enemy"]:
                            if attr in ignore:
                                continue
                            if ATTR_DATA["enemy"][attr]["type"] == "bool":
                                if "ignore_if_true" in ATTR_DATA["enemy"][attr] and ENEMY_DATA[enemy][attr]:
                                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_true"])
                                elif "ignore_if_false" in ATTR_DATA["enemy"][attr] and not ENEMY_DATA[enemy][attr]:
                                    ignore.extend(ATTR_DATA["enemy"][attr]["ignore_if_false"])
                    with open(path.join(GAME_FOLDER, "enemies.json"), 'w') as out_file:
                        json.dump(ENEMY_DATA, out_file, indent=4)
                    for enemy in ENEMY_DATA:
                        ENEMY_DATA[enemy]["image"] = pg.image.load(
                            path.join(ENEMIES_IMG_FOLDER, "{}.png".format(enemy)))
                        ENEMY_DATA[enemy]["death_sound"] = pg.mixer.Sound(
                            path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(enemy)))
                    for tower in TOWER_DATA:
                        for stage in range(3):
                            if "gun_image" in TOWER_DATA[tower]["stages"][stage]:
                                TOWER_DATA[tower]["stages"][stage].pop("gun_image")
                            if "base_image" in TOWER_DATA[tower]["stages"][stage]:
                                TOWER_DATA[tower]["stages"][stage].pop("base_image")
                            if "bullet_image" in TOWER_DATA[tower]["stages"][stage]:
                                TOWER_DATA[tower]["stages"][stage].pop("bullet_image")
                            if "shoot_sound" in TOWER_DATA[tower]["stages"][stage]:
                                TOWER_DATA[tower]["stages"][stage].pop("shoot_sound")
                            if "image" in TOWER_DATA[tower]["stages"][stage]:
                                TOWER_DATA[tower]["stages"][stage].pop("image")
                            ignore = []
                            for attr in ATTR_DATA["stage"]:
                                if attr in ignore:
                                    continue
                                if ATTR_DATA["stage"][attr]["type"] == "bool":
                                    if "ignore_if_true" in ATTR_DATA["stage"][attr] and TOWER_DATA[tower]["stages"][stage][attr]:
                                        ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_true"])
                                    elif "ignore_if_false" in ATTR_DATA["stage"][attr] and not TOWER_DATA[tower]["stages"][stage][attr]:
                                        ignore.extend(ATTR_DATA["stage"][attr]["ignore_if_false"])
                    with open(path.join(GAME_FOLDER, "towers.json"), 'w') as out_file:
                        json.dump(TOWER_DATA, out_file, indent=4)
                    for tower in TOWER_DATA:
                        for stage in range(3):
                            TOWER_DATA[tower]["stages"][stage]["base_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_base" + str(stage) + ".png"))

                            temp_base = TOWER_DATA[tower]["stages"][stage]["base_image"].copy()
                            base = TOWER_DATA[tower]["stages"][stage]["base_image"]
                            if not TOWER_DATA[tower]["stages"][stage]["area_of_effect"]:
                                TOWER_DATA[tower]["stages"][stage]["bullet_image"] = pg.image.load(
                                    path.join(TOWERS_IMG_FOLDER, tower + "_bullet" + str(stage) + ".png"))

                                if TOWER_DATA[tower]["stages"][stage]["rotating"]:
                                    TOWER_DATA[tower]["stages"][stage]["gun_image"] = pg.image.load(
                                        path.join(TOWERS_IMG_FOLDER, tower + "_gun" + str(stage) + ".png"))
                                    temp_base.blit(TOWER_DATA[tower]["stages"][stage]["gun_image"],
                                                   TOWER_DATA[tower]["stages"][stage]["gun_image"].get_rect(
                                                       center=base.get_rect().center))

                            TOWER_DATA[tower]["stages"][stage]["image"] = temp_base
                            
                            if TOWER_DATA[tower]["stages"][stage]["area_of_effect"]:
                                if TOWER_DATA[tower]["stages"][stage]["aoe_buff"]:
                                    continue # skip adding shoot sounds for AOE buff towers
                            
                            TOWER_DATA[tower]["stages"][stage]["shoot_sound"] = pg.mixer.Sound(
                                path.join(TOWERS_AUD_FOLDER, "{}.wav".format(tower)))
                    
                    update_sfx_vol() # Has to be called since saving settings resets enemy and tower sounds
                    
                    self.save_text = "Settings Saved!"
                    pg.time.set_timer(pg.USEREVENT + 1, 2000)
                    return_val = -2

                elif self.done_button_rect.collidepoint(offset):
                    return_val = "menu"

                elif self.reload_tower_button_rect.collidepoint(offset):
                    return_val = "reload_towers"

                elif self.reload_enemy_button_rect.collidepoint(offset):
                    return_val = "reload_enemies"

                else:
                    if self.attributes[0].minus_button_rect.collidepoint(offset):
                        if self.attributes[0].change_val(self.attributes[0].current_value - 1):
                            return_val = "scroll_position"
                    elif self.attributes[0].plus_button_rect.collidepoint(offset):
                        if self.attributes[0].change_val(self.attributes[0].current_value + 1):
                            return_val = "scroll_position"

                    else:
                        for attr in self.attributes[self.attributes[0].current_value:self.attributes[0].current_value + self.max_attrs]:
                            if attr.disabled:
                                continue
                            if attr.type == "float":
                                if attr.minus_button_rect.collidepoint(offset):
                                    if attr.change_val(round(attr.current_value - attr.increment, attr.dp)):
                                        return_val = attr
                                    break
                                elif attr.plus_button_rect.collidepoint(offset):
                                    if attr.change_val(round(attr.current_value + attr.increment, attr.dp)):
                                        return_val = attr
                                    break
                            elif attr.type == "bool":
                                if attr.x_button_rect.collidepoint(offset):
                                    if attr.change_val(not attr.current_value):
                                        return_val = attr
                                    break
                            elif attr.type == "select":
                                if attr.back_button_rect.collidepoint(offset):
                                    if attr.change_val(attr.current_value - 1):
                                        return_val = attr
                                    break
                                elif attr.next_button_rect.collidepoint(offset):
                                    if attr.change_val(attr.current_value + 1):
                                        return_val = attr
                                    break
                            elif attr.type == "string":
                                if attr.textbox_rect.collidepoint(offset):
                                    if not attr.over:
                                        attr.over = True
                                        return_val = attr
                                    break
                                elif attr.enter_button_rect.collidepoint(offset):
                                    attr.over = False
                                    return_val = attr.name
                                    break
                                elif attr.over:
                                    attr.over = False
                                    return_val = attr
                                    break
        elif event.type == pg.KEYDOWN:
            for attr in self.attributes:
                if attr.type == "string" and attr.over:
                    if event.key == pg.K_BACKSPACE:
                        if attr.current_value != "" and attr.change_val(attr.current_value[:-1]):
                            return_val = attr
                    elif event.key == pg.K_RETURN:
                        if attr.current_value != "":
                            attr.over = False
                            return_val = attr.name
                    else:
                        if attr.change_val(attr.current_value + event.unicode):
                            return_val = attr
                    break
        if isinstance(return_val, Attribute) and return_val.reload_on_change:
            return_val = return_val.name
                            
        if event.type == pg.USEREVENT + 1:
            self.save_text = "Save Settings"
            pg.time.set_timer(pg.USEREVENT + 1, 0)
            return_val = -2
            
        return return_val

class Attribute():
    def __init__(self, name, data, value, disabled = True, reload_on_change = False):
        self.name = name
        self.data = data
        self.type = data["type"]
        if self.type == "float":
            self.min = data["min"]
            self.max = data["max"]
            self.dp = data["dp"]
            self.increment = data["increment"]
        elif self.type == "select":
            self.values = data["values"]
        elif self.type == "string":
            self.over = False
        self.reload_on_change = reload_on_change
        self.disabled = False
        self.change_val(value)
        self.disabled = disabled

    def draw(self):
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.2))
        surf_list = []
        if self.type == "string":
            texts = textwrap.fill(self.current_value, 40 - round(MENU_TEXT_SIZE / 30))
            attr_texts = []
            height = 0
            width = 0
            
            if self.current_value == "":
                if self.over:
                    attr_text = font.render("{}...".format(self.name), 1, WHITE)
                else:
                    attr_text = font.render("{}...".format(self.name), 1, LIGHT_GREY)
                attr_texts.append(attr_text)
                height = attr_text.get_height()
                width = attr_text.get_width()
            else:
                for text in texts.split("\n"):
                    attr_text = font.render(text, 1, WHITE)
                    attr_texts.append(font.render(text, 1, WHITE))
                    
                    height += attr_text.get_height()
                    width = max(width, attr_text.get_width())
                
            textbox = pg.transform.scale(LEVEL_BUTTON_IMG, (width + MENU_OFFSET * 4, height)).copy().convert_alpha()
            
            y = 0
            for attr_text in attr_texts:
                textbox.blit(attr_text, (MENU_OFFSET, y))
                y += attr_text.get_height()
                
            self.textbox_rect = textbox.get_rect()
            surf_list.append(textbox)

            if not self.disabled:
                enter_text = font.render("enter", 1, WHITE)
                enter_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
                    round(enter_text.get_rect().width * 1.5), enter_text.get_rect().height)).copy().convert_alpha()
                enter_button.blit(enter_text, enter_text.get_rect(center=enter_button.get_rect().center))
                self.enter_button_rect = enter_button.get_rect()
                surf_list.append(enter_button)

        else:
            attr_text = font.render(self.name.replace('_', ' '), 1, WHITE)
            surf_list.append(attr_text)

            if self.type == "float":
                if not self.disabled:
                    button = pg.transform.scale(LEVEL_BUTTON_IMG, (attr_text.get_rect().height, attr_text.get_rect().height))
                    minus_button = button.copy().convert_alpha()
                    minus_text = font.render('-', 1, WHITE)
                    minus_button.blit(minus_text, minus_text.get_rect(center = minus_button.get_rect().center))
                    surf_list.append(minus_button)
                    self.minus_button_rect = minus_button.get_rect()

                cur_val_text = font.render(str(self.current_value), 1, WHITE)
                surf_list.append(cur_val_text)

                if not self.disabled:
                    plus_button = button.copy().convert_alpha()
                    plus_text = font.render('+', 1, WHITE)
                    plus_button.blit(plus_text, plus_text.get_rect(center = plus_button.get_rect().center))
                    surf_list.append(plus_button)
                    self.plus_button_rect = plus_button.get_rect()

            elif self.type == "bool":
                button = pg.transform.scale(LEVEL_BUTTON_IMG, (attr_text.get_rect().height, attr_text.get_rect().height)).copy().convert_alpha()
                if self.current_value == True:
                    x_text = font.render('X', 1, WHITE)
                    button.blit(x_text, x_text.get_rect(center = button.get_rect().center))
                surf_list.append(button)
                self.x_button_rect = button.get_rect()

            elif self.type == "select":
                if not self.disabled:
                    back_text = font.render("<", 1, WHITE)
                    back_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
                    back_text.get_rect().height, back_text.get_rect().height)).copy().convert_alpha()
                    back_button.blit(back_text, back_text.get_rect(center=back_button.get_rect().center))
                    self.back_button_rect = back_button.get_rect()
                    surf_list.append(back_button)

                text = font.render(clean_title(self.values[self.current_value]), 1, WHITE)
                surf_list.append(text)

                if not self.disabled:
                    next_text = font.render(">", 1, WHITE)
                    next_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
                    next_text.get_rect().height, next_text.get_rect().height)).copy().convert_alpha()
                    next_button.blit(next_text, next_text.get_rect(center=next_button.get_rect().center))
                    self.next_button_rect = next_button.get_rect()
                    surf_list.append(next_button)

        width = MENU_OFFSET
        for i, surf in enumerate(surf_list):
            if not self.disabled:
                if self.type == "float" and (i == 1 or i == 3):
                    if i == 1:
                        self.minus_button_rect.x = width
                    else:
                        self.plus_button_rect.x = width
                elif self.type == "bool" and i == 1:
                    self.x_button_rect.x = width
                elif self.type == "select" and (i == 1 or i == 3):
                    if i == 1:
                        self.back_button_rect.x = width
                    else:
                        self.next_button_rect.x = width
                elif self.type == "string":
                    if i == 0:
                        self.textbox_rect.x = width
                    else:
                        self.enter_button_rect.x = width
            width += surf.get_rect().width + MENU_OFFSET
        
        if self.type == "string":
            height = self.textbox_rect.h
        else:
            height = attr_text.get_rect().height
        
        attr_surf = pg.Surface((width, height))
        attr_surf.fill(DARK_GREY)

        temp_w = MENU_OFFSET
        for surf in surf_list:
            attr_surf.blit(surf, (temp_w, 0))
            temp_w += surf.get_rect().width + MENU_OFFSET

        return attr_surf

    def fix_offset(self, width, height):
        if not self.disabled:
            if self.type == "float":
                self.minus_button_rect = self.minus_button_rect.move(width, height)
                self.plus_button_rect = self.plus_button_rect.move(width, height)
            elif self.type == "bool":
                self.x_button_rect = self.x_button_rect.move(width, height)
            elif self.type == "select":
                self.back_button_rect = self.back_button_rect.move(width, height)
                self.next_button_rect = self.next_button_rect.move(width, height)
            elif self.type == "string":
                self.textbox_rect = self.textbox_rect.move(width, height)
                self.enter_button_rect = self.enter_button_rect.move(width, height)

    def change_val(self, value):
        if self.disabled:
            return False

        if self.type == "int" or self.type == "float":
            if value < self.min or value > self.max:
                return False

        elif self.type == "bool":
            if not isinstance(value, bool):
                return False

        elif self.type == "select":
            if value < 0:
                value = len(self.values) + value

            elif value > len(self.values) - 1:
                value = value - len(self.values)

        self.current_value = value
        return True
