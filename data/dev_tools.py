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
    def __init__(self, clock, map):
        self.clock = clock
        self.map = TiledMap(path.join(MAP_FOLDER, "{}_test.tmx".format(map)))
        super().load_data()

    def new(self):
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

        self.starts = [Start(self.clock, self, 0, self.enemy_names[self.current_enemy], -1, 0, 0.5)]
        self.pathfinder = Pathfinder()
        self.pathfinder.clear_nodes(self.map.get_map())
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def load_ui(self):
        self.ui = DevUI()
        self.ui.new_attr(Attribute("tower_name", {
            "type": "string",
            "values": self.tower_names
        }, self.current_tower))
        self.ui.new_attr(Attribute("tower_level", {
            "type": "float",
            "min": 0,
            "max": 2,
            "dp": 0,
            "increment": 1
        }, self.current_level))
        self.ui.new_attr(Attribute("enemy_name", {
            "type": "string",
            "values": self.enemy_names
        }, self.current_enemy))

    def reload_attrs(self):
        attrs = self.ui.get_attrs()
        self.current_tower = attrs.pop("tower_name")
        self.current_level = attrs.pop("tower_level")
        self.current_enemy = attrs.pop("enemy_name")
        return attrs

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

        return surface

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            result = self.ui.event_button((event.pos[0] - self.map.width, event.pos[1] - self.create_button_rect.height - MENU_OFFSET * 2))
            if result == -1:
                return -1

            name = result.name
            if name == "menu":
                return name

            elif name == "tower_name" or name == "tower_level" or name == "enemy_name":
                return -3

            return -2
        return -1

class TowerPreview(DevClass):
    def __init__(self, clock):
        super().__init__(clock, "tower")
        super().load_data()

    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().new()
        self.new_tower_name = ""
        self.over_tower_button = False
        self.load_ui()

    def load_ui(self):
        super().load_ui()

        for attr in ATTR_DATA["tower"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["tower"][attr], TOWER_DATA[self.tower_names[self.current_tower]][self.current_level][attr]))

        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def get_attr_surf(self):
        height = MENU_OFFSET
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))

        new_tower = []
        width = MENU_OFFSET
        if self.new_tower_name == "":
            if self.over_tower_button:
                tower_text = font.render("tower name...", 1, WHITE)
            else:
                tower_text = font.render("tower name...", 1, LIGHTGREY)
        else:
            tower_text = font.render(self.new_tower_name, 1, WHITE)
        tower_button = pg.transform.scale(LEVEL_BUTTON_IMG, (tower_text.get_rect().width + MENU_OFFSET * 4, tower_text.get_rect().height)).copy().convert_alpha()
        tower_button.blit(tower_text, tower_text.get_rect(center = tower_button.get_rect().center))
        self.tower_button_rect = tower_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += tower_button.get_rect().width + MENU_OFFSET
        new_tower.append(tower_button)

        create_text = font.render("create tower", 1, WHITE)
        create_button = pg.transform.scale(LEVEL_BUTTON_IMG, (round(create_text.get_rect().width * 1.5), create_text.get_rect().height)).copy().convert_alpha()
        create_button.blit(create_text, create_text.get_rect(center = create_button.get_rect().center))
        self.create_button_rect = create_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += create_button.get_rect().width + MENU_OFFSET
        new_tower.append(create_button)

        surf = pg.Surface((width, tower_text.get_rect().height))
        surf.fill(DARKGREY)
        temp_w = MENU_OFFSET
        for item in new_tower:
            surf.blit(item, (temp_w, 0))
            temp_w += item.get_rect().width + MENU_OFFSET

        height += surf.get_height()
        ui_surf = self.ui.get_ui()
        height += ui_surf.get_height()
        if ui_surf.get_width() > width:
            width = ui_surf.get_width()

        self.attr_surf = pg.Surface((width, height))
        self.attr_surf.fill(DARKGREY)
        self.attr_surf.blit(surf, (0, MENU_OFFSET))
        self.attr_surf.blit(ui_surf, (0, surf.get_height() + MENU_OFFSET))

    def reload_attrs(self):
        attrs = super().reload_attrs()
        for attr in attrs:
            TOWER_DATA[self.tower_names[self.current_tower]][self.current_level][attr] = attrs[attr]
        self.reload_towers()
        self.reload_enemies()
        self.get_attr_surf()

    def draw(self):
        surface = super().draw()
        combo_surf = pg.Surface((surface.get_rect().width + self.attr_surf.get_rect().width,
                                 max(surface.get_rect().height, self.attr_surf.get_rect().height)))
        combo_surf.blit(surface, (0, 0))
        combo_surf.blit(self.attr_surf, (surface.get_rect().width, 0))
        return combo_surf

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            return result

        if result == -3:
            super().reload_attrs()
            self.load_ui()

        if result <= -2:
            self.reload_attrs()
            return -1

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.create_button_rect.collidepoint(event.pos):
                    self.over_tower_button = False
                    self.create_new_tower()
                    self.new_tower_name = ""
                    self.get_attr_surf()
                    return -1

                elif self.tower_button_rect.collidepoint(event.pos):
                    self.over_tower_button = True
                    return -1

        elif event.type == pg.KEYDOWN:
            if self.over_tower_button:
                if event.key == pg.K_BACKSPACE:
                    self.new_tower_name = self.new_tower_name[:-1]
                    self.get_attr_surf()
                elif event.key == pg.K_RETURN:
                    self.create_new_tower()
                    self.new_tower_name = ""
                    self.get_attr_surf()
                else:
                    self.new_tower_name += event.unicode
                    self.get_attr_surf()
            return -1

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
        self.load_ui()

class EnemyPreview(DevClass):
    def __init__(self, clock):
        super().__init__(clock, "enemy")
        super().load_data()

    def new(self, args):
        # initialize all variables and do all the setup for a new game
        super().new()
        self.new_enemy_name = ""
        self.over_enemy_button = False
        self.load_ui()

    def load_ui(self):
        super().load_ui()

        for attr in ATTR_DATA["enemy"]:
            self.ui.new_attr(Attribute(attr, ATTR_DATA["enemy"][attr],
                                       ENEMY_DATA[self.enemy_names[self.current_enemy]][attr]))
        self.reload_enemies()
        self.reload_towers()
        self.get_attr_surf()

    def get_attr_surf(self):
        height = MENU_OFFSET
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))

        new_enemy = []
        width = MENU_OFFSET
        if self.new_enemy_name == "":
            if self.over_enemy_button:
                enemy_text = font.render("enemy name...", 1, WHITE)
            else:
                enemy_text = font.render("enemy name...", 1, LIGHTGREY)
        else:
            enemy_text = font.render(self.new_enemy_name, 1, WHITE)
        enemy_button = pg.transform.scale(LEVEL_BUTTON_IMG, (enemy_text.get_rect().width + MENU_OFFSET * 4, enemy_text.get_rect().height)).copy().convert_alpha()
        enemy_button.blit(enemy_text, enemy_text.get_rect(center=enemy_button.get_rect().center))
        self.enemy_button_rect = enemy_button.get_rect(x=self.map.width + MENU_OFFSET + width,
                                                       y=height + MENU_OFFSET)
        width += enemy_button.get_rect().width + MENU_OFFSET
        new_enemy.append(enemy_button)

        create_text = font.render("create enemy", 1, WHITE)
        create_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(create_text.get_rect().width * 1.5), create_text.get_rect().height)).copy().convert_alpha()
        create_button.blit(create_text, create_text.get_rect(center=create_button.get_rect().center))
        self.create_button_rect = create_button.get_rect(x=self.map.width + MENU_OFFSET + width,
                                                         y=height + MENU_OFFSET)
        width += create_button.get_rect().width + MENU_OFFSET
        new_enemy.append(create_button)

        surf = pg.Surface((width, enemy_text.get_rect().height))
        surf.fill(DARKGREY)
        temp_w = MENU_OFFSET
        for item in new_enemy:
            surf.blit(item, (temp_w, 0))
            temp_w += item.get_rect().width + MENU_OFFSET

        height += surf.get_height()
        ui_surf = self.ui.get_ui()
        height += ui_surf.get_height()
        if ui_surf.get_width() > width:
            width = ui_surf.get_width()

        self.attr_surf = pg.Surface((width, height))
        self.attr_surf.fill(DARKGREY)
        self.attr_surf.blit(surf, (0, MENU_OFFSET))
        self.attr_surf.blit(ui_surf, (0, surf.get_height() + MENU_OFFSET))

    def reload_attrs(self):
        attrs = super().reload_attrs()
        for attr in attrs:
            ENEMY_DATA[self.enemy_names[self.current_enemy]][attr] = attrs[attr]
        self.reload_towers()
        self.reload_enemies()
        self.get_attr_surf()

    def draw(self):
        surface = super().draw()
        combo_surf = pg.Surface((surface.get_rect().width + self.attr_surf.get_rect().width,
                                 max(surface.get_rect().height, self.attr_surf.get_rect().height)))
        combo_surf.blit(surface, (0, 0))
        combo_surf.blit(self.attr_surf, (surface.get_rect().width, 0))
        return combo_surf

    def event(self, event):
        result = super().event(event)
        if isinstance(result, str):
            return result

        if result == -3:
            super().reload_attrs()
            self.load_ui()

        if result <= -2:
            self.reload_attrs()
            return -1

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.create_button_rect.collidepoint(event.pos):
                    self.over_enemy_button = False
                    self.create_new_enemy()
                    self.new_enemy_name = ""
                    self.load_ui()
                    return -1

                elif self.enemy_button_rect.collidepoint(event.pos):
                    self.over_enemy_button = True
                    return -1

        elif event.type == pg.KEYDOWN:
            if self.over_enemy_button:
                if event.key == pg.K_BACKSPACE:
                    self.new_enemy_name = self.new_enemy_name[:-1]
                    self.get_attr_surf()
                elif event.key == pg.K_RETURN:
                    self.create_new_enemy()
                    self.new_enemy_name = ""
                    self.get_attr_surf()
                else:
                    self.new_enemy_name += event.unicode
                    self.get_attr_surf()
            return -1

        return -1

    def create_new_enemy(self):
        ENEMY_DATA[self.new_enemy_name] = {}
        for attr in ATTR_DATA["enemy"]:
            ENEMY_DATA[self.new_enemy_name][attr] = ATTR_DATA["enemy"][attr]["default"]
        ENEMY_DATA[self.new_enemy_name]["image"] = pg.image.load(path.join(ENEMIES_IMG_FOLDER, "{}.png".format(self.new_enemy_name)))
        ENEMY_DATA[self.new_enemy_name]["death_sound_path"] = path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(self.new_enemy_name))
        self.enemy_names = list(ENEMY_DATA.keys())
        self.current_enemy = self.enemy_names.index(self.new_enemy_name)
        self.load_ui()

class DevUI():
    def __init__(self):
        self.attributes = []

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
            attr.fix_height(height)
            height += attr_surf.get_height() + MENU_OFFSET
            if attr_surf.get_width() > width:
                width = attr_surf.get_width()
            surf_list.append(attr_surf)

        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))
        save_text = font.render("Save Settings", 1, WHITE)
        save_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(save_text.get_rect().width * 1.5), save_text.get_height())).copy().convert_alpha()
        save_button.blit(save_text, save_text.get_rect(center=save_button.get_rect().center))
        self.save_button_rect = save_button.get_rect()
        self.save_button_rect.y = height + MENU_OFFSET
        self.save_button_rect.x = MENU_OFFSET

        height += save_button.get_rect().height + MENU_OFFSET

        done_text = font.render("Done", 1, WHITE)
        done_button = pg.transform.scale(LEVEL_BUTTON_IMG, (
        round(done_text.get_rect().width * 1.5), done_text.get_height())).copy().convert_alpha()
        done_button.blit(done_text, done_text.get_rect(center=done_button.get_rect().center))
        self.done_button_rect = done_button.get_rect()
        self.done_button_rect.y = self.save_button_rect.y
        self.done_button_rect.x = self.save_button_rect.width + MENU_OFFSET * 2

        save_surfs = [save_button, done_button]

        surf = pg.Surface((width, height))
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

    def event_button(self, offset):
        if self.save_button_rect.collidepoint(offset):
            for enemy in ENEMY_DATA:
                ENEMY_DATA[enemy].pop("image")
                ENEMY_DATA[enemy].pop("death_sound_path")
            with open(path.join(GAME_FOLDER, "enemies.json"), 'w') as out_file:
                json.dump(ENEMY_DATA, out_file, indent=4)
            for enemy in ENEMY_DATA:
                ENEMY_DATA[enemy]["image"] = pg.image.load(
                    path.join(ENEMIES_IMG_FOLDER, "{}.png".format(enemy)))
                ENEMY_DATA[enemy]["death_sound_path"] = path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(enemy))
            for tower in TOWER_DATA:
                for level in range(3):
                    TOWER_DATA[tower][level].pop("gun_image", None)
                    TOWER_DATA[tower][level].pop("base_image", None)
                    TOWER_DATA[tower][level].pop("bullet_image", None)
                    TOWER_DATA[tower][level].pop("shoot_sound_path", None)
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
            return -1

        elif self.done_button_rect.collidepoint(offset):
            return "menu"

        else:
            for attr in self.attributes:
                if attr.type == "int" or attr.type == "float":
                    if attr.minus_button_rect.collidepoint(offset):
                        if attr.change_val(round(attr.current_value - attr.increment, attr.dp)):
                            return attr
                    elif attr.plus_button_rect.collidepoint(offset):
                        if attr.change_val(round(attr.current_value + attr.increment, attr.dp)):
                            return attr
                elif attr.type == "bool":
                    if attr.x_button_rect.collidepoint(offset):
                        if attr.change_val(not attr.current_value):
                            return attr
                elif attr.type == "string":
                    if attr.back_button_rect.collidepoint(offset):
                        if attr.change_val(attr.current_value - 1):
                            return attr
                    elif attr.next_button_rect.collidepoint(offset):
                        if attr.change_val(attr.current_value + 1):
                            return attr
            return -1

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
        elif self.type == "string":
            self.values = data["values"]
        self.change_val(value)

    def draw(self):
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))
        surf_list = []
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

        elif self.type == "string":
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
            elif self.type == "string" and (i == 1 or i == 3):
                if i == 1:
                    self.back_button_rect.x = width
                else:
                    self.next_button_rect.x = width
            width += surf.get_rect().width + MENU_OFFSET

        attr_surf = pg.Surface((width, attr_text.get_rect().height))
        attr_surf.fill(DARKGREY)

        temp_w = MENU_OFFSET
        for surf in surf_list:
            attr_surf.blit(surf, (temp_w, 0))
            temp_w += surf.get_rect().width + MENU_OFFSET

        return attr_surf

    def fix_height(self, value):
        if self.type == "float":
            self.minus_button_rect.y += value
            self.plus_button_rect.y += value
        elif self.type == "bool":
            self.x_button_rect.y += value
        elif self.type == "string":
            self.back_button_rect.y += value
            self.next_button_rect.y += value

    def change_val(self, value):
        if self.type == "int" or self.type == "float":
            if value < self.min or value > self.max:
                return False

        elif self.type == "bool":
            if not isinstance(value, bool):
                return False

        elif self.type == "string":
            if value < 0:
                value = len(self.values) + value

            elif value > len(self.values) - 1:
                value = value - len(self.values)

        self.current_value = value
        return True
