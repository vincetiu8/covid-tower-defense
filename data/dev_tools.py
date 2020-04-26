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

class Tower_Preview(Game):
    def __init__(self):
        self.tower_names = list(TOWER_DATA.keys())
        self.current_tower = 0
        self.current_level = 0
        self.map = TiledMap(path.join(MAP_FOLDER, "tower_test.tmx"))
        super().load_data()
        self.new()
        self.load_attrs()

    def new(self):
        # initialize all variables and do all the setup for a new game
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
                self.map.add_tower(tile_from_xcoords(tile_object.x, self.map.tilesize), tile_from_xcoords(tile_object.y, self.map.tilesize), Tower(self, tile_object.x, tile_object.y, self.tower_names[self.current_tower]))

        self.starts = [Start(self, 0, 'common_cold', -1, 0, 0.5)]
        self.pathfinder = Pathfinder()
        self.pathfinder.clear_nodes(self.map.get_map())
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def load_attrs(self):
        self.attributes = []
        for attr in ATTR_DATA["tower"]:
            attr_class = Attribute("tower", self.tower_names[self.current_tower], attr)
            self.attributes.append(attr_class)
            attr_class.update_level(self.current_level)
        self.get_attr_surf()

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

        combo_surf = pg.Surface((surface.get_rect().width + self.attr_surf.get_rect().width, max(surface.get_rect().height, self.attr_surf.get_rect().height)))
        combo_surf.blit(surface, (0, 0))
        combo_surf.blit(self.attr_surf, (surface.get_rect().width, 0))

        return combo_surf

    def get_attr_surf(self):
        height = MENU_OFFSET
        attr_surfaces = []
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))

        title = []
        width = MENU_OFFSET
        back_text = font.render("<", 1, WHITE)
        back_button = pg.transform.scale(LEVEL_BUTTON_IMG, (back_text.get_rect().height, back_text.get_rect().height)).copy().convert_alpha()
        back_button.blit(back_text, back_text.get_rect(center = back_button.get_rect().center))
        self.back_button_rect = back_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += back_button.get_rect().width + MENU_OFFSET
        title.append(back_button)

        tower_text = font.render(self.tower_names[self.current_tower].replace('_', ' '), 1, WHITE)
        width += tower_text.get_rect().width + MENU_OFFSET
        title.append(tower_text)

        next_text = font.render(">", 1, WHITE)
        next_button = pg.transform.scale(LEVEL_BUTTON_IMG, (next_text.get_rect().height, next_text.get_rect().height)).copy().convert_alpha()
        next_button.blit(next_text, next_text.get_rect(center = next_button.get_rect().center))
        self.next_button_rect = next_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += next_button.get_rect().width + MENU_OFFSET
        title.append(next_button)

        down_text = font.render("-", 1, WHITE)
        down_button = pg.transform.scale(LEVEL_BUTTON_IMG, (down_text.get_rect().height, down_text.get_rect().height)).copy().convert_alpha()
        down_button.blit(down_text, down_text.get_rect(center = down_button.get_rect().center))
        self.down_button_rect = down_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += down_button.get_rect().width + MENU_OFFSET
        title.append(down_button)

        level_text = font.render(str(self.current_level), 1, WHITE)
        width += level_text.get_rect().width + MENU_OFFSET
        title.append(level_text)

        up_text = font.render("+", 1, WHITE)
        up_button = pg.transform.scale(LEVEL_BUTTON_IMG, (up_text.get_rect().height, up_text.get_rect().height)).copy().convert_alpha()
        up_button.blit(up_text, up_text.get_rect(center = up_button.get_rect().center))
        self.up_button_rect = up_button.get_rect(x = self.map.width + MENU_OFFSET + width, y = height + MENU_OFFSET)
        width += up_button.get_rect().width + MENU_OFFSET
        title.append(up_button)

        surf = pg.Surface((width, tower_text.get_rect().height))
        surf.fill(DARKGREY)
        temp_w = MENU_OFFSET
        for item in title:
            surf.blit(item, (temp_w, 0))
            temp_w += item.get_rect().width + MENU_OFFSET
        attr_surfaces.append(surf)
        height += surf.get_rect().height + MENU_OFFSET

        for attr in self.attributes:
            surf = attr.draw()
            attr_surfaces.append(surf)
            if attr.type == "int" or attr.type == "float":
                attr.minus_button_rect.y = height + MENU_OFFSET
                attr.minus_button_rect.x += self.map.width + MENU_OFFSET
                attr.plus_button_rect.y = height + MENU_OFFSET
                attr.plus_button_rect.x += self.map.width + MENU_OFFSET
            elif attr.type == "bool":
                attr.x_button_rect.y = height + MENU_OFFSET
                attr.x_button_rect.x += self.map.width + MENU_OFFSET
            height += surf.get_rect().height + MENU_OFFSET
            if surf.get_rect().width > width:
                width = surf.get_rect().width

        save_text = font.render("Save Settings", 1, WHITE)
        save_button = pg.transform.scale(LEVEL_BUTTON_IMG, (round(save_text.get_rect().width * 1.5), round(save_text.get_rect().height * 1.5))).copy().convert_alpha()
        save_button.blit(save_text, save_text.get_rect(center = save_button.get_rect().center))
        attr_surfaces.append(save_button)
        self.save_button_rect = save_button.get_rect()
        self.save_button_rect.y = height + MENU_OFFSET
        self.save_button_rect.x = self.map.width + MENU_OFFSET

        height += save_button.get_rect().height + MENU_OFFSET

        self.attr_surf = pg.Surface((width, height))
        self.attr_surf.fill(DARKGREY)
        temp_h = MENU_OFFSET
        for surf in attr_surfaces:
            self.attr_surf.blit(surf, (0, temp_h))
            temp_h += surf.get_rect().height + MENU_OFFSET

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

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.save_button_rect.collidepoint(event.pos):
                    for tower in TOWER_DATA:
                        for level in range(3):
                            TOWER_DATA[tower][level].pop("gun_image", None)
                            TOWER_DATA[tower][level].pop("base_image", None)
                            TOWER_DATA[tower][level].pop("bullet_image", None)
                            TOWER_DATA[tower][level].pop("shoot_sound_path", None)
                            TOWER_DATA[tower][level].pop("image", None)
                    with open(path.join(GAME_FOLDER, "towers.json"), 'w') as out_file:
                        json.dump(TOWER_DATA, out_file)
                    for tower in TOWER_DATA:
                        for level in range(3):
                            TOWER_DATA[tower][level]["gun_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_gun" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["base_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_base" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["bullet_image"] = pg.image.load(
                                path.join(TOWERS_IMG_FOLDER, tower + "_bullet" + str(level) + ".png"))
                            TOWER_DATA[tower][level]["shoot_sound_path"] = path.join(TOWERS_AUD_FOLDER, "{}.wav".format(tower))
                            temp_base = TOWER_DATA[tower][level]["base_image"].copy()
                            temp_base.blit(TOWER_DATA[tower][level]["gun_image"],
                                           TOWER_DATA[tower][level]["gun_image"].get_rect(
                                               center=TOWER_DATA[tower][level]["base_image"].get_rect().center))
                            TOWER_DATA[tower][level]["image"] = temp_base
                    return

                elif self.back_button_rect.collidepoint(event.pos):
                    self.current_tower -= 1
                    if self.current_tower < 0:
                        self.current_tower = len(self.tower_names) - 1
                    self.reload_towers()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.next_button_rect.collidepoint(event.pos):
                    self.current_tower += 1
                    if self.current_tower == len(self.tower_names):
                        self.current_tower = 0
                    self.reload_towers()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.enemy_back_button_rect.collidepoint(event.pos):
                    self.current_enemy -= 1
                    if self.current_enemy < 0:
                        self.current_enemy = len(self.enemy_names) - 1
                    self.reload_enemies()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.enemy_next_button_rect.collidepoint(event.pos):
                    self.current_enemy += 1
                    if self.current_enemy == len(self.enemy_names):
                        self.current_enemy = 0
                    self.reload_enemies()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.down_button_rect.collidepoint(event.pos) and self.current_level > 0:
                    self.current_level -= 1
                    self.reload_towers()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.up_button_rect.collidepoint(event.pos) and self.current_level < 2:
                    self.current_level += 1
                    self.reload_towers()
                    self.load_attrs()
                    self.get_attr_surf()
                    return

                elif self.create_button_rect.collidepoint(event.pos):
                    self.over_tower_button = False
                    self.create_new_tower()
                    self.reload_towers()
                    self.load_attrs()
                    self.new_tower_name = ""
                    self.get_attr_surf()
                    return

                if self.tower_button_rect.collidepoint(event.pos):
                    self.over_tower_button = True
                    return

                else:
                    self.over_tower_button = False
                    for attr in self.attributes:
                        if attr.type == "int" or attr.type == "float":
                            if attr.minus_button_rect.collidepoint(event.pos):
                                if attr.change_val(round(attr.current_value - attr.increment, attr.dp)):
                                    self.get_attr_surf()
                                    for tower in self.towers:
                                        tower.load_tower_data()
                            elif attr.plus_button_rect.collidepoint(event.pos):
                                if attr.change_val(round(attr.current_value + attr.increment, attr.dp)):
                                    self.get_attr_surf()
                                    for tower in self.towers:
                                        tower.load_tower_data()
                        elif attr.type == "bool":
                            if attr.x_button_rect.collidepoint(event.pos):
                                if attr.change_val(not attr.current_value):
                                    self.get_attr_surf()
                                    for tower in self.towers:
                                        tower.load_tower_data()

        elif event.type == pg.KEYDOWN:
            if self.over_tower_button:
                if event.key == pg.K_BACKSPACE:
                    self.new_tower_name = self.new_tower_name[:-1]
                    self.get_attr_surf()
                elif event.key == pg.K_RETURN:
                    self.create_new_tower()
                    self.load_attrs()
                    self.new_tower_name = ""
                    self.get_attr_surf()
                    self.reload_towers()
                else:
                    self.new_tower_name += event.unicode
                    self.get_attr_surf()

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

    def reload_enemies(self):
        for start in self.starts:
            start.enemy_type = self.enemy_names[self.current_enemy]


class Enemy_Preview(Game):
    def __init__(self):
        self.enemy_names = list(ENEMY_DATA.keys())
        self.current_enemy = 0
        self.current_level = 0
        self.tower_names = list(TOWER_DATA.keys())
        self.current_tower = 0
        self.map = TiledMap(path.join(MAP_FOLDER, "enemy_test.tmx"))
        super().load_data()
        self.new()
        self.load_attrs()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()

        self.new_enemy_name = ""
        self.over_enemy_button = False
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
                self.map.add_tower(tile_from_xcoords(tile_object.x, self.map.tilesize), tile_from_xcoords(tile_object.y, self.map.tilesize), Tower(self, tile_object.x, tile_object.y, self.tower_names[self.current_tower]))

        self.starts = [Start(self, 0, self.enemy_names[self.current_enemy], -1, 0, 0.5)]
        self.pathfinder = Pathfinder()
        self.pathfinder.clear_nodes(self.map.get_map())
        self.make_stripped_path(pg.Surface((self.map.width, self.map.height)))
        self.draw_tower_bases(pg.Surface((self.map.width, self.map.height)))

    def load_attrs(self):
        self.attributes = []
        for attr in ATTR_DATA["enemy"]:
            attr_class = Attribute("enemy", self.enemy_names[self.current_enemy], attr)
            self.attributes.append(attr_class)
            attr_class.update_level(-1)
        self.get_attr_surf()

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

        combo_surf = pg.Surface((surface.get_rect().width + self.attr_surf.get_rect().width, max(surface.get_rect().height, self.attr_surf.get_rect().height)))
        combo_surf.blit(surface, (0, 0))
        combo_surf.blit(self.attr_surf, (surface.get_rect().width, 0))
        
        if self.save_button_rect.collidepoint(event.pos):
            for tower in TOWER_DATA:
                for level in range(3):
                    TOWER_DATA[tower][level].pop("gun_image", None)
                    TOWER_DATA[tower][level].pop("base_image", None)
                    TOWER_DATA[tower][level].pop("bullet_image", None)
                    TOWER_DATA[tower][level].pop("shoot_sound_path", None)
                    TOWER_DATA[tower][level].pop("image", None)
            with open(path.join(GAME_FOLDER, "towers.json"), 'w') as out_file:
                json.dump(TOWER_DATA, out_file)
            for tower in TOWER_DATA:
                for level in range(3):
                    TOWER_DATA[tower][level]["gun_image"] = pg.image.load(
                        path.join(TOWERS_IMG_FOLDER, tower + "_gun" + str(level) + ".png"))
                    TOWER_DATA[tower][level]["base_image"] = pg.image.load(
                        path.join(TOWERS_IMG_FOLDER, tower + "_base" + str(level) + ".png"))
                    TOWER_DATA[tower][level]["bullet_image"] = pg.image.load(
                        path.join(TOWERS_IMG_FOLDER, tower + "_bullet" + str(level) + ".png"))
                    TOWER_DATA[tower][level]["shoot_sound_path"] = path.join(TOWERS_AUD_FOLDER, "{}.wav".format(tower))
                    temp_base = TOWER_DATA[tower][level]["base_image"].copy()
                    temp_base.blit(TOWER_DATA[tower][level]["gun_image"],
                                   TOWER_DATA[tower][level]["gun_image"].get_rect(
                                       center=TOWER_DATA[tower][level]["base_image"].get_rect().center))
                    TOWER_DATA[tower][level]["image"] = temp_base

        elif self.back_button_rect.collidepoint(event.pos):
            self.current_tower -= 1
            if self.current_tower < 0:
                self.current_tower = len(self.tower_names) - 1
            self.reload_towers()
            self.load_attrs()
            self.get_attr_surf()

        elif self.next_button_rect.collidepoint(event.pos):
            self.current_tower += 1
            if self.current_tower == len(self.tower_names):
                self.current_tower = 0
            self.reload_towers()
            self.load_attrs()
            self.get_attr_surf()

        elif self.down_button_rect.collidepoint(event.pos) and self.current_level > 0:
            self.current_level -= 1
            self.reload_towers()
            self.load_attrs()
            self.get_attr_surf()

        elif self.up_button_rect.collidepoint(event.pos) and self.current_level < 2:
            self.current_level += 1
            self.reload_towers()
            self.load_attrs()
            self.get_attr_surf()
        else:
            for attr in self.attributes:
                if attr.type == "int" or attr.type == "float":
                    if attr.minus_button_rect.collidepoint(event.pos):
                        if attr.change_val(round(attr.current_value - attr.increment, attr.dp)):
                            self.get_attr_surf()
                            for tower in self.towers:
                                tower.load_tower_data()
                    elif attr.plus_button_rect.collidepoint(event.pos):
                        if attr.change_val(round(attr.current_value + attr.increment, attr.dp)):
                            self.get_attr_surf()
                            for tower in self.towers:
                                tower.load_tower_data()
                elif attr.type == "bool":
                    if attr.x_button_rect.collidepoint(event.pos):
                        if attr.change_val(not attr.current_value):
                            self.get_attr_surf()
                            for tower in self.towers:
                                tower.load_tower_data()

class Attribute():
    def __init__(self, obj_type, obj, attr):
        self.obj_type = obj_type
        self.obj = obj
        self.attr = attr
        data = ATTR_DATA[obj_type][attr]
        self.type = data["type"]
        if "min" in ATTR_DATA[obj_type][attr]:
            self.min = ATTR_DATA[obj_type][attr]["min"]
        if "max" in ATTR_DATA[obj_type][attr]:
            self.max = ATTR_DATA[obj_type][attr]["max"]
        if "dp" in ATTR_DATA[obj_type][attr]:
            self.dp = ATTR_DATA[obj_type][attr]["dp"]
        if "increment" in ATTR_DATA[obj_type][attr]:
            self.increment = ATTR_DATA[obj_type][attr]["increment"]
        if obj_type == "enemy":
            self.data = ENEMY_DATA[obj]
        elif obj_type == "tower":
            self.data = TOWER_DATA[obj]

    def update_level(self, level):
        self.level = level
        if level == -1:
            self.current_value = self.data[self.attr]
        else:
            self.current_value = self.data[level][self.attr]

    def draw(self):
        font = pg.font.Font(FONT, round(MENU_TEXT_SIZE * 1.5))
        surf_list = []
        if self.attr == "upgrade_cost" and self.level == 0:
            attr_text = font.render("buy cost", 1, WHITE)
        else:
            attr_text = font.render(self.attr.replace('_', ' '), 1, WHITE)
        surf_list.append(attr_text)

        if self.type == "int" or self.type == "float":
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
            plus_button.blit(plus_text, minus_text.get_rect(center = minus_button.get_rect().center))
            surf_list.append(plus_button)
            self.plus_button_rect = plus_button.get_rect()

        elif self.type == "bool":
            button = pg.transform.scale(LEVEL_BUTTON_IMG, (attr_text.get_rect().height, attr_text.get_rect().height)).copy().convert_alpha()
            if self.current_value == True:
                x_text = font.render('X', 1, WHITE)
                button.blit(x_text, x_text.get_rect(center = button.get_rect().center))
            surf_list.append(button)
            self.x_button_rect = button.get_rect()

        width = MENU_OFFSET
        for i, surf in enumerate(surf_list):
            if (self.type == "int" or self.type == "float") and (i == 1 or i == 3):
                if i == 1:
                    self.minus_button_rect.x = width
                else:
                    self.plus_button_rect.x = width
            elif self.type == "bool" and i == 1:
                self.x_button_rect.x = width
            width += surf.get_rect().width + MENU_OFFSET

        attr_surf = pg.Surface((width, attr_text.get_rect().height))
        attr_surf.fill(DARKGREY)

        temp_w = MENU_OFFSET
        for surf in surf_list:
            attr_surf.blit(surf, (temp_w, 0))
            temp_w += surf.get_rect().width + MENU_OFFSET

        return attr_surf

    def change_val(self, value):
        if self.type == "int" or self.type == "float":
            if value < self.min or value > self.max:
                return False

        elif self.type == "bool":
            if not isinstance(value, bool):
                return False

        if self.obj_type == "enemy":
            ENEMY_DATA[self.obj][self.attr] = value
        elif self.obj_type == "tower":
            TOWER_DATA[self.obj][self.level][self.attr] = value

        self.current_value = value
        return True