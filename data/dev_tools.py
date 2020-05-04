import pygame as pg
from data.main import Game
from data.tilemap import *
from data.pathfinding import *
from data.game import *
from os import path
from data.settings import TOWER_DATA
import data.settings as settings
import json
from copy import deepcopy

class DevClass(Game):
    def __init__(self, clock):
        self.clock = clock

    def reload_level(self, map):
        self.map = TiledMap(path.join(MAP_FOLDER, "{}.tmx".format(map)))
        super().load_data()

    def new(self):
        #self.clock = pg.time.Clock()
        self.tower_names = list(TOWER_DATA.keys())
        self.enemy_names = list(ENEMY_DATA.keys())
        self.current_tower = 0
        self.current_level = 0
        self.current_enemy = 0

        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()

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
        self.pathfinder = Pathfinder()
        self.pathfinder.clear_nodes(self.map.get_map())
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def load_ui(self):
        self.ui = DevUI()
        self.ui.new_attr(Attribute("tower_name", {
            "type": "select",
            "values": self.tower_names
        }, self.current_tower))
        self.ui.new_attr(Attribute("tower_level", {
            "type": "float",
            "min": 0,
            "max": 2,
            "dp": 0,
            "increment": 1
        }, self.current_level))

    def reload_towers(self):
        for x, list in enumerate(self.map.get_tower_map()):
            for y, tower in enumerate(list):
                if tower != None:
                    temp_tower = Tower(self, tower.rect.x, tower.rect.y, self.tower_names[self.current_tower])
                    temp_tower.stage = self.current_level
                    temp_tower.load_tower_data()
                    self.map.remove_tower(x, y)
                    self.map.add_tower(x, y, temp_tower)
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def reload_enemies(self):
        for start in self.starts:
            start.enemy_type = self.enemy_names[self.current_enemy]

    def update(self):
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()

    def draw(self):
        #self.clock.tick()
        surface = pg.Surface((self.map.width, self.map.height))
        surface.fill((0, 0, 0))

        surface.blit(self.map_img, self.map_rect)

        for start in self.starts:
            pg.draw.rect(surface, GREEN, start.rect)
        for goal in self.goals:
            pg.draw.rect(surface, GREEN, goal.rect)

        surface.blit(self.path_surf, self.path_surf.get_rect())
        surface.blit(self.tower_bases_surf,
                     self.tower_bases_surf.get_rect())

        for tower in self.towers:
            rotated_image = pg.transform.rotate(tower.gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            surface.blit(rotated_image, new_rect)

        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)
            pg.draw.rect(surface, GREEN, enemy.get_hp_rect())

        for projectile in self.projectiles:
            surface.blit(projectile.image, projectile.rect)

        surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.blit(self.camera.apply_image((surface)), self.camera.apply_tuple((0, 0)))

        ui_pos = (SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)
        if self.ui.active:
            ui = self.attr_surf
            ui_rect = ui.get_rect(topright=ui_pos)
            surf.blit(ui, ui_rect)
            surf.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright=ui_rect.topleft))
        else:
            surf.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright=ui_pos))
        
        #self.clock.tick()
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
            return result

        name = result.name

        if name == "tower_name" or name == "tower_level" or name == "enemy_name":
            return -3

        return -2

class TowerPreview(DevClass):
    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().reload_level("tower_test")
        super().load_data()
        super().new()
        self.starts = [Start(self.clock, self, start, self.enemy_names[self.current_enemy], -1, 0, 0.5) for start in range(len(self.start_data))]
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))
        self.new_tower_name = ""
        self.load_ui()

    def load_ui(self):
        super().load_ui()
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy))
        self.ui.new_attr(Attribute("new_tower_name", {"type": "string"}, ""))

        for attr in ATTR_DATA["tower"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["tower"][attr], TOWER_DATA[self.tower_names[self.current_tower]][self.current_level][attr]))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def get_attr_surf(self):
        self.attr_surf = self.ui.get_ui()

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        reload = False
        self.current_enemy = attrs.pop("enemy_name")
        self.new_tower_name = attrs.pop("new_tower_name")
        for attr in attrs:
            if attr == "tower_name":
                if self.current_tower != attrs[attr]:
                    reload = True
            elif attr == "tower_level":
                if self.current_level != attrs[attr]:
                    reload = True
            else:
                TOWER_DATA[self.tower_names[self.current_tower]][self.current_level][attr] = attrs[attr]
        if reload:
            self.current_tower = attrs["tower_name"]
            self.current_level = attrs["tower_level"]

        self.reload_towers()
        self.reload_enemies()
        self.get_attr_surf()

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            if result == "menu":
                return result
            elif result == "new_tower_name":
                self.create_new_tower()
                self.load_ui()
            else:
                self.reload_attrs()

        elif result == -3:
            self.reload_attrs()
            self.load_ui()

        elif result == -2:
            self.reload_attrs()

        return -1

    def create_new_tower(self):
        TOWER_DATA[self.new_tower_name] = []
        for level in range(3):
            TOWER_DATA[self.new_tower_name].append({})
            for attr in ATTR_DATA["tower"]:
                TOWER_DATA[self.new_tower_name][level][attr] = ATTR_DATA["tower"][attr]["default"]
            TOWER_DATA[self.new_tower_name][level]["gun_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_gun" + str(level) + ".png"))
            TOWER_DATA[self.new_tower_name][level]["base_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_base" + str(level) + ".png"))
            TOWER_DATA[self.new_tower_name][level]["bullet_image"] = pg.image.load(
                path.join(TOWERS_IMG_FOLDER, self.new_tower_name + "_bullet" + str(level) + ".png"))
            TOWER_DATA[self.new_tower_name][level]["shoot_sound_path"] = path.join(TOWERS_AUD_FOLDER, "{}.wav".format(self.new_tower_name))
            temp_base = TOWER_DATA[self.new_tower_name][level]["base_image"].copy()
            temp_base.blit(TOWER_DATA[self.new_tower_name][level]["gun_image"],
                           TOWER_DATA[self.new_tower_name][level]["gun_image"].get_rect(
                               center=TOWER_DATA[self.new_tower_name][level]["base_image"].get_rect().center))
            TOWER_DATA[self.new_tower_name][level]["image"] = temp_base
        self.tower_names = list(TOWER_DATA.keys())
        self.current_tower = self.tower_names.index(self.new_tower_name)
        self.current_level = 0

class EnemyPreview(DevClass):
    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().reload_level("enemy_test")
        super().load_data()
        super().new()
        self.starts = [Start(self.clock, self, start, self.enemy_names[self.current_enemy], -1, 0, 0.5) for start in range(len(self.start_data))]
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))
        self.new_enemy_name = ""
        self.load_ui()

    def load_ui(self):
        super().load_ui()
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "select",
            "values": self.enemy_names
        }, self.current_enemy))
        self.ui.new_attr(Attribute("new_enemy_name", {"type": "string"}, ""))

        for attr in ATTR_DATA["enemy"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr],
                                       ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]))
        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def get_attr_surf(self):
        self.attr_surf = self.ui.get_ui()

    def reload_attrs(self):
        reload = False
        attrs = self.ui.get_attrs()
        self.current_tower = attrs.pop("tower_name")
        self.current_level = attrs.pop("tower_level")
        self.new_enemy_name = attrs.pop("new_enemy_name")
        for attr in attrs:
            if attr == "enemy_name":
                if self.current_enemy != attrs[attr]:
                    reload = True
            else:
                ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] = attrs[attr]
        if reload:
            self.current_enemy = attrs["enemy_name"]

        self.reload_towers()
        self.reload_enemies()
        self.get_attr_surf()

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            if result == "menu":
                return result
            elif result == "new_enemy_name":
                self.create_new_enemy()
                self.load_ui()
            else:
                self.reload_attrs()

        elif result == -3:
            self.reload_attrs()
            self.load_ui()

        elif result == -2:
            self.reload_attrs()

        return -1

    def create_new_enemy(self):
        ENEMY_DATA[self.new_enemy_name] = {}
        for attr in ATTR_DATA["enemy"]:
            ENEMY_DATA[self.new_enemy_name][attr] = ATTR_DATA["enemy"][attr]["default"]
        ENEMY_DATA[self.new_enemy_name]["image"] = pg.image.load(path.join(ENEMIES_IMG_FOLDER, "{}.png".format(self.new_enemy_name)))
        ENEMY_DATA[self.new_enemy_name]["death_sound_path"] = path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(self.new_enemy_name))
        self.enemy_names = list(ENEMY_DATA.keys())
        self.current_enemy = self.enemy_names.index(self.new_enemy_name)

class LevelPreview(DevClass):
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
        self.starts = [Start(self.clock, self, start, self.enemy_names[self.current_enemy], -1, 0, 0.5) for start in range(len(self.start_data))]
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))

    def new(self, args):
        # initialize all variables and do all the setup for a new game
        self.reload_level()
        self.load_ui()

    def load_ui(self):
        super().load_ui()

        self.ui.new_attr(Attribute("level",
                                   {"type": "float",
                                    "min": 0,
                                    "max": len(LEVEL_DATA),
                                    "increment": 1,
                                    "dp": 0
                                    }, self.level))
        for attr in ATTR_DATA["level"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["level"][attr],
                                       LEVEL_DATA[self.level][attr]))

        self.ui.new_attr(Attribute("wave",
                                   {"type": "float",
                                    "min": 0,
                                    "max": len(LEVEL_DATA[self.level]["waves"]),
                                    "increment": 1,
                                    "dp": 0
                                    }, self.wave))
        self.ui.new_attr(Attribute("sub_wave",
                                    {"type": "float",
                                     "min": 0,
                                     "max": len(LEVEL_DATA[self.level]["waves"][self.wave]),
                                     "increment": 1,
                                     "dp": 0
                                     }, self.sub_wave))

        for attr in ATTR_DATA["sub_wave"]:
            temp_dat = ATTR_DATA["sub_wave"][attr].copy()
            temp_val = LEVEL_DATA[self.level]["waves"][self.wave][self.sub_wave][attr]
            if attr == "start":
                temp_dat["max"] = len(self.start_data) - 1
            elif attr == "enemy_type":
                temp_dat["values"] = self.enemy_types
                temp_val = self.enemy_types.index(temp_val)
            self.ui.new_attr(Attribute(attr, temp_dat, temp_val))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def reload_enemies(self):
        self.starts.clear()
        self.enemies = pg.sprite.Group()
        for s in LEVEL_DATA[self.level]["waves"][self.wave]:
            self.starts.append(Start(self.clock, self, s["start"], s["enemy_type"], s["enemy_count"], s["spawn_delay"], s["spawn_rate"]))

    def update(self):
        super().update()
        if self.current_wave_done() and len(self.enemies) == 0:
            self.reload_enemies()

    def get_attr_surf(self):
        self.attr_surf = self.ui.get_ui()

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        load = False
        create_level = False
        create_wave = False
        create_sub_wave = False
        self.current_tower = attrs.pop("tower_name")
        self.current_level = attrs.pop("tower_level")
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
            print(LEVEL_DATA[self.level])

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
            else:
                self.reload_attrs()

        elif result == -3:
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
    def __init__(self):
        self.attributes = []
        self.active = True

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
        width = 0
        for attr in self.attributes:
            attr_surf = attr.draw()
            attr.fix_offset(MENU_OFFSET, height)
            height += attr_surf.get_height() + MENU_OFFSET
            if attr_surf.get_width() > width:
                width = attr_surf.get_width()
            surf_list.append(attr_surf)

        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.2))
        save_text = font.render("Save Settings", 1, WHITE)
        save_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(save_text.get_rect().width * 1.5), save_text.get_height())).copy().convert_alpha()
        save_button.blit(save_text, save_text.get_rect(center=save_button.get_rect().center))
        self.save_button_rect = save_button.get_rect()
        self.save_button_rect.y = height - MENU_OFFSET
        self.save_button_rect.x = MENU_OFFSET

        height += save_button.get_rect().height + MENU_OFFSET

        done_text = font.render("Done", 1, WHITE)
        done_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(done_text.get_rect().width * 1.5), done_text.get_height())).copy().convert_alpha()
        done_button.blit(done_text, done_text.get_rect(center=done_button.get_rect().center))
        self.done_button_rect = done_button.get_rect()
        self.done_button_rect.y = self.save_button_rect.y
        self.done_button_rect.x = self.save_button_rect.width + MENU_OFFSET * 2

        if self.save_button_rect.width + self.done_button_rect.width + MENU_OFFSET * 3 > width:
            width = self.save_button_rect.width + self.done_button_rect.width + MENU_OFFSET * 3

        save_surfs = [save_button, done_button]

        surf = pg.Surface((width + MENU_OFFSET, height))
        surf.fill(DARKGREY)
        height = MENU_OFFSET
        for attr in surf_list:
            surf.blit(attr, (MENU_OFFSET, height))
            height += attr.get_height() + MENU_OFFSET

        width = MENU_OFFSET
        for save_surf in save_surfs:
            surf.blit(save_surf, (width, height))
            width += save_surf.get_rect().width + MENU_OFFSET

        return surf

    def event(self, event, w):
        return_val = -1
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                offset = (event.pos[0] - w, event.pos[1] - MENU_OFFSET)
                if self.save_button_rect.collidepoint(offset):
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
                        if "death_sound_path" in ENEMY_DATA[enemy]:
                            ENEMY_DATA[enemy].pop("death_sound_path")
                    with open(path.join(GAME_FOLDER, "enemies.json"), 'w') as out_file:
                        json.dump(ENEMY_DATA, out_file, indent=4)
                    for enemy in ENEMY_DATA:
                        ENEMY_DATA[enemy]["image"] = pg.image.load(
                            path.join(ENEMIES_IMG_FOLDER, "{}.png".format(enemy)))
                        ENEMY_DATA[enemy]["death_sound_path"] = path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(enemy))
                    for tower in TOWER_DATA:
                        for level in range(3):
                            if "gun_image" in TOWER_DATA[tower][level]:
                                TOWER_DATA[tower][level].pop("gun_image", None)
                            if "base_image" in TOWER_DATA[tower][level]:
                                TOWER_DATA[tower][level].pop("base_image", None)
                            if "bullet_image" in TOWER_DATA[tower][level]:
                                TOWER_DATA[tower][level].pop("bullet_image", None)
                            if "shoot_sound_path" in TOWER_DATA[tower][level]:
                                TOWER_DATA[tower][level].pop("shoot_sound_path", None)
                            if "image" in TOWER_DATA[tower][level]:
                                TOWER_DATA[tower][level].pop("image", None)
                    with open(path.join(GAME_FOLDER, "towers.json"), 'w') as out_file:
                        json.dump(TOWER_DATA, out_file, indent=4)
                    for tower in TOWER_DATA:
                        for level in range(3):
                            TOWER_DATA[tower][level]["gun_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_gun" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["base_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_base" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["bullet_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_bullet" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["shoot_sound_path"] = path.join(TOWERS_AUD_FOLDER,
                                                                                     "{}.wav".format(tower))
                            temp_base = TOWER_DATA[tower][level]["base_image"].copy()
                            temp_base.blit(TOWER_DATA[tower][level]["gun_image"],
                                           TOWER_DATA[tower][level]["gun_image"].get_rect(
                                               center=TOWER_DATA[tower][level]["base_image"].get_rect().center))
                            TOWER_DATA[tower][level]["image"] = temp_base
                    return_val = -1

                elif self.done_button_rect.collidepoint(offset):
                    return_val = "menu"

                else:
                    for attr in self.attributes:
                        if attr.type == "float":
                            if attr.minus_button_rect.collidepoint(offset):
                                if attr.change_val(round(attr.current_value - attr.increment, attr.dp)):
                                    return_val = attr
                            elif attr.plus_button_rect.collidepoint(offset):
                                if attr.change_val(round(attr.current_value + attr.increment, attr.dp)):
                                    return_val = attr
                        elif attr.type == "bool":
                            if attr.x_button_rect.collidepoint(offset):
                                if attr.change_val(not attr.current_value):
                                    return_val = attr
                        elif attr.type == "select":
                            if attr.back_button_rect.collidepoint(offset):
                                if attr.change_val(attr.current_value - 1):
                                    return_val = attr
                            elif attr.next_button_rect.collidepoint(offset):
                                if attr.change_val(attr.current_value + 1):
                                    return_val = attr
                        elif attr.type == "string":
                            if attr.textbox_rect.collidepoint(offset):
                                if not attr.over:
                                    attr.over = True
                                    return_val = attr
                            elif attr.enter_button_rect.collidepoint(offset):
                                attr.over = False
                                return_val = attr.name
                            elif attr.over:
                                attr.over = False
                                return_val = attr
        elif event.type == pg.KEYDOWN:
            for attr in self.attributes:
                if attr.type == "string" and attr.over:
                    if event.key == pg.K_BACKSPACE and attr.current_value != "":
                        if attr.change_val(attr.current_value[:-1]):
                            return_val = attr
                    elif event.key == pg.K_RETURN and attr.current_value != "":
                        attr.over = False
                        return_val = attr.name
                    else:
                        if attr.change_val(attr.current_value + event.unicode):
                            return_val = attr
        return return_val

class Attribute():
    def __init__(self, name, data, value):
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
        self.change_val(value)

    def draw(self):
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.2))
        surf_list = []
        if self.type == "string":
            if self.current_value == "":
                if self.over:
                    attr_text = font.render("{}...".format(self.name), 1, WHITE)
                else:
                    attr_text = font.render("{}...".format(self.name), 1, LIGHTGREY)
            else:
                attr_text = font.render(self.current_value, 1, WHITE)
            textbox = pg.transform.scale(LEVEL_BUTTON_IMG, (
            attr_text.get_rect().width + MENU_OFFSET * 4, attr_text.get_rect().height)).copy().convert_alpha()
            textbox.blit(attr_text, attr_text.get_rect(center=textbox.get_rect().center))
            self.textbox_rect = textbox.get_rect()
            surf_list.append(textbox)

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
                button = pg.transform.scale(LEVEL_BUTTON_IMG, (attr_text.get_rect().height, attr_text.get_rect().height))
                minus_button = button.copy().convert_alpha()
                minus_text = font.render('-', 1, WHITE)
                minus_button.blit(minus_text, minus_text.get_rect(center = minus_button.get_rect().center))
                surf_list.append(minus_button)
                self.minus_button_rect = minus_button.get_rect()

                cur_val_text = font.render(str(self.current_value), 1, WHITE)
                surf_list.append(cur_val_text)

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
                back_text = font.render("<", 1, WHITE)
                back_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
                back_text.get_rect().height, back_text.get_rect().height)).copy().convert_alpha()
                back_button.blit(back_text, back_text.get_rect(center=back_button.get_rect().center))
                self.back_button_rect = back_button.get_rect()
                surf_list.append(back_button)

                text = font.render(self.values[self.current_value], 1, WHITE)
                surf_list.append(text)

                next_text = font.render(">", 1, WHITE)
                next_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
                next_text.get_rect().height, next_text.get_rect().height)).copy().convert_alpha()
                next_button.blit(next_text, next_text.get_rect(center=next_button.get_rect().center))
                self.next_button_rect = next_button.get_rect()
                surf_list.append(next_button)

        width = MENU_OFFSET
        for i, surf in enumerate(surf_list):
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

        attr_surf = pg.Surface((width, attr_text.get_rect().height))
        attr_surf.fill(DARKGREY)

        temp_w = MENU_OFFSET
        for surf in surf_list:
            attr_surf.blit(surf, (temp_w, 0))
            temp_w += surf.get_rect().width + MENU_OFFSET

        return attr_surf

    def fix_offset(self, width, height):
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
