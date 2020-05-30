from data.tilemap import *
from data.enemies import *
from data.pathfinding import *
from data.game_misc import *
from data.towers import *
from data.display import *

import random

vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Game(Display):
    def __init__(self, clock):
        super().__init__()
        self.clock = clock
        
        self.paused = False
        self.in_a_wave = False
        
        self.starts = []
        self.game_done_event = pg.event.Event(pg.USEREVENT)
        
        self.ui_pos = None

    def load_data(self):
        self.map_img = self.map.make_map()
        self.map_objects = self.map.make_objects()
        self.map_rect = self.map_img.get_rect()

    def load_level_data(self):
        self.level_data = LEVEL_DATA[self.level]
        self.max_wave = len(self.level_data["waves"])
        
    def new(self, args):
        self.level = args[0]
        to_resume = args[1]
        self.available_towers = args[2]
        
        if not to_resume:
            self.new_game()
    
    def new_game(self):
        self.map = TiledMap(path.join(MAP_FOLDER, "{}.tmx".format(list(BODY_PARTS)[LEVEL_DATA[self.level]["body_part"]])))
        self.load_data()
        self.load_level_data()
        
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.explosions = pg.sprite.Group()

        self.current_tower = None
        self.protein = SAVE_DATA["game_attrs"]["starting_protein"]["value"]
        self.lives = SAVE_DATA["game_attrs"]["lives"]["value"]

        self.wave = -1  # only updated at the start of prepare_next_wave()
        self.cause_of_death = "IB"
        self.start_data = []
        self.map.clear_map()
        
        self.time_passed = 0

        width = round(self.map.width / self.map.tilesize)
        height = round(self.map.height / self.map.tilesize)
        arteries = [[1 for row in range(height)] for col in range(width)]
        veins = [[1 for row in range(height)] for col in range(width)]
        artery_entrances = [[1 for row in range(height)] for col in range(width)]
        vein_entrances = [[1 for row in range(height)] for col in range(width)]

        for tile_object in self.map.tmxdata.objects:
            if "start" in tile_object.name:
                self.start_data.insert(int(tile_object.name[5:]),
                                       pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height))
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                            0)  # make start tile a wall so you can't place a tower on it
                                                # this does not affect the path finding algo
            elif tile_object.name == "goal":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                            1)  # make start tile a wall so you can't place a tower on it
                                                # this does not affect the path finding algo
                        Goal(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == "artery":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        arteries[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "vein":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        veins[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "artery_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        artery_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "vein_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        vein_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0

        for start in self.start_data:
            for x in range(tile_from_xcoords(start.width, self.map.tilesize)):
                for y in range(tile_from_xcoords(start.height, self.map.tilesize)):
                    self.map.set_valid_tower_tile(tile_from_xcoords(start.x, self.map.tilesize) + x, tile_from_xcoords(start.y, self.map.tilesize) + y, 0)

        self.ui = UI(self, 200, 10)
        self.pathfinder = Pathfinder(
            arteries = arteries,
            artery_entrances = artery_entrances,
            veins = veins,
            vein_entrances = vein_entrances,
            base_map = self.map.get_map())
        
        self.node_is_in_path = [[]]
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.pathfinder.clear_nodes(self.map.get_map())
        self.textbox = Textbox(self)
        self.prepare_next_wave()
        self.draw_tower_bases_wrapper()
        self.make_stripped_path_wrapper()

    def update(self):
        # update portion of the game loop
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()
        self.ui.update()
        self.explosions.update()
        self.textbox.update()

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.camera.move(25, 0)

        elif keys[pg.K_RIGHT]:
            self.camera.move(-25, 0)

        elif keys[pg.K_UP]:
            self.camera.move(0, 25)

        elif keys[pg.K_DOWN]:
            self.camera.move(0, -25)

        if self.lives <= 0:
            pg.event.post(self.game_done_event)

        if self.text:
            if len(self.enemies) > 0:
                return
            elif len(self.texts) == 0:
                self.prepare_next_wave()
                self.start_next_wave()
            return

        if not self.in_a_wave and self.wave > 0:
            self.time_passed += self.clock.get_time()
            if self.time_passed >= WAVE_DELAY * 1000:
                self.start_next_wave()

        if self.current_wave_done() and self.in_a_wave:
            if self.wave < self.max_wave - 1:
                self.prepare_next_wave()                
            elif len(self.enemies) == 0:
                pg.event.post(self.game_done_event)

    def current_wave_done(self):
        for start in self.starts:
            if not start.is_done_spawning():
                return False
        return True
    
    def prepare_next_wave(self):
        self.wave += 1
        if isinstance(self.level_data["waves"][self.wave][0], str):
            self.text = True
            self.texts = [text for text in self.level_data["waves"][self.wave]]
            print(self.texts)
            self.ui.set_next_wave_btn(False)
            self.textbox.enabled = True
            self.textbox.set_text(self.texts[0])

        else:
            self.text = False
            self.textbox.enabled = False
            self.in_a_wave = False
            self.ui.set_next_wave_btn(True)
            self.time_passed = 0

            self.starts.clear()
            for i in self.level_data["waves"][self.wave]:
                self.starts.append(
                    Start(self, i["start"], i["enemy_type"], i["enemy_count"],
                          i["spawn_delay"], i["spawn_rate"]))

            self.make_stripped_path_wrapper()

    def start_next_wave(self):
        self.in_a_wave = True
        self.ui.set_next_wave_btn(False)

        for start in self.starts:
            start.enable_spawning()

    #     def draw_grid(self):
    #         for x in range(0, self.map.width, self.map.tilesize):
    #             pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, self.map.height))
    #         for y in range(0, self.map.height, self.map.tilesize):
    #             pg.draw.line(self.screen, LIGHTGREY, (0, y), (self.map.width, y))

    def draw(self):
        self.fill((0, 0, 0))

        self.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))

        self.blit(self.camera.apply_image(self.path_surf), self.camera.apply_tuple((0, 0)))

        self.blit(self.camera.apply_image(self.tower_bases_surf),
                     self.camera.apply_rect(self.tower_bases_surf.get_rect()))

        for tower in self.towers:
            if tower.area_of_effect or not tower.rotating:
                continue
            rotated_image = pg.transform.rotate(tower.gun_image, math.degrees(tower.rotation))
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            self.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))

        for enemy in self.enemies:
            self.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            hp_surf = enemy.get_hp_surf()
            if hp_surf != None:
                self.blit(self.camera.apply_image(hp_surf), self.camera.apply_rect(hp_surf.get_rect(center=(enemy.rect.center[0], enemy.rect.center[1] - 15))))

        for projectile in self.projectiles:
            self.blit(self.camera.apply_image(projectile.image), self.camera.apply_rect(projectile.rect))
        
        self.draw_aoe_sprites(self)
        self.blit(self.camera.apply_image(self.aoe_surf), self.camera.apply_tuple((0, 0)))

        for explosion in self.explosions:
            self.blit(self.camera.apply_image(explosion.get_surf()), self.camera.apply_tuple((explosion.x, explosion.y)))

        self.blit(self.camera.apply_image(self.map_objects), self.camera.apply_rect(self.map_rect))

        if self.current_tower != None:
            self.draw_tower_preview()

        if self.ui.tower != None and not self.ui.tower.area_of_effect:
            tower_range_img = pg.Surface((self.ui.tower.true_range * 2, self.ui.tower.true_range * 2)).convert_alpha()
            tower_range_img.fill(BLANK)
            pg.draw.circle(tower_range_img, HALF_WHITE, (self.ui.tower.true_range, self.ui.tower.true_range), self.ui.tower.true_range)
            self.blit(self.camera.apply_image(tower_range_img), self.camera.apply_rect(tower_range_img.get_rect(center=self.ui.tower.rect.center)))

        self.ui_pos = [self.get_size()[0] - self.ui.offset, self.ui.offset]
        if self.ui.active:
            self.ui_pos[0] -= self.ui.width
            ui = self.ui.ui
            ui_rect = ui.get_rect(topleft = self.ui_pos)
            self.blit(ui, ui_rect)
            self.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright = ui_rect.topleft))
        else:
            self.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright = (SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)))
        
        if len(self.enemies) == 0 and self.textbox.enabled:
            self.blit(self.textbox, (MENU_OFFSET, SCREEN_HEIGHT - self.textbox.yoffset))
        
        return self

    def make_stripped_path_wrapper(self):
        self.make_stripped_path(self)

    def make_stripped_path(self, surface):
        self.node_is_in_path = [[False for i in range(len(self.map.get_map()[0]))] for j in range(len(self.map.get_map()))]
        self.path_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.path_surf.fill((0, 0, 0, 0))

        done = []
        for start in self.starts:
            if start.start in done:
                continue
            done.append(start.start)
            xpos = tile_from_xcoords(start.rect.x, self.map.tilesize)
            ypos = tile_from_xcoords(start.rect.y, self.map.tilesize)
            for x in range(tile_from_xcoords(start.rect.w, self.map.tilesize)):
                for y in range(tile_from_xcoords(start.rect.h, self.map.tilesize)):
                    flying = ENEMY_DATA[start.enemy_type]["flying"]
                    path = self.pathfinder.astar(((xpos + x, ypos + y), 0), self.goals, flying)
                    self.stripped_path = []
                    for i, node in enumerate(path):
                        if node[1] == 0: # not artery or vein
                            self.node_is_in_path[node[0][0]][node[0][1]] = True
                            
                        if (i < len(path) - 1):
                            diff_x_after = path[i + 1][0][0] - node[0][0]
                            diff_y_after = path[i + 1][0][1] - node[0][1]
                            if (diff_x_after == 0 and diff_y_after == 0):
                                continue
                        self.stripped_path.append(node[0])
                    for i, node in enumerate(self.stripped_path):
                        if (i > 0 and i < len(self.stripped_path) - 1):
                            image = None
                            diff_x_before = self.stripped_path[i - 1][0] - node[0]
                            diff_x_after = self.stripped_path[i + 1][0] - node[0]
                            diff_y_before = self.stripped_path[i - 1][1] - node[1]
                            diff_y_after = self.stripped_path[i + 1][1] - node[1]

                            if diff_x_before == 0 and diff_x_after == 0:  # up <--> down
                                image = PATH_VERTICAL_IMG
                            elif diff_y_before == 0 and diff_y_after == 0:  # left <--> right
                                image = PATH_HORIZONTAL_IMG
                            elif (diff_x_before == 1 and diff_y_after == 1) or (
                                    diff_y_before == 1 and diff_x_after == 1):  # right <--> down
                                image = PATH_CORNER1_IMG
                            elif (diff_x_before == -1 and diff_y_after == 1) or (
                                    diff_y_before == 1 and diff_x_after == -1):  # left <--> down
                                image = PATH_CORNER2_IMG
                            elif (diff_x_before == 1 and diff_y_after == -1) or (
                                    diff_y_before == -1 and diff_x_after == 1):  # right <--> up
                                image = PATH_CORNER3_IMG
                            elif (diff_x_before == -1 and diff_y_after == -1) or (
                                    diff_y_before == -1 and diff_x_after == -1):  # left <--> up
                                image = PATH_CORNER4_IMG
                            else:
                                print("PATH DRAWING ERROR")  # this should never occur

                            if flying:
                                new_image = image.copy()
                                new_image.fill(GREEN, None, pg.BLEND_RGBA_MULT)
                            else:
                                new_image = image
                            self.path_surf.blit(new_image, pg.Rect(node[0] * self.map.tilesize, node[1] * self.map.tilesize,
                                                               self.map.tilesize, self.map.tilesize))

    def draw_tower_bases_wrapper(self):
        self.draw_tower_bases(self)

    def draw_tower_bases(self, surface):
        self.tower_bases_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.tower_bases_surf.fill((0, 0, 0, 0))
        for tower in self.towers:
            self.tower_bases_surf.blit(tower.base_image, tower.rect)
            
        self.draw_aoe_sprites(surface)
                
    def draw_aoe_sprites(self, surface):
        self.aoe_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.aoe_surf.fill((0, 0, 0, 0))
        for tower in self.towers:
            if tower.area_of_effect:
                s = pg.Surface(tower.aoe_sprite.rect.size, pg.SRCALPHA)
                s.fill(AURA_COLORS[tower.aura_color])
                self.aoe_surf.blit(s, tower.aoe_sprite.rect, special_flags=pg.BLEND_RGBA_MAX)

    def draw_tower_preview(self):
        mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
        towerxy = (
            round_to_tilesize(mouse_pos[0], self.map.tilesize), round_to_tilesize(mouse_pos[1], self.map.tilesize))
        tower_tile = (
            tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize))
        tower = TOWER_DATA[self.current_tower]["stages"][0]
        pos = self.map.get_node(tower_tile[0], tower_tile[1])

        if pos != -1:
            tower_range = tower["range"]
            if tower["area_of_effect"]:
                tower_range_img = pg.Surface((tower_range, tower_range)).convert_alpha()
                tower_range_img.fill(AURA_COLORS[tower["aura_color"]])

            else:
                tower_range_img = pg.Surface((tower_range * 2, tower_range * 2)).convert_alpha()
                tower_range_img.fill(BLANK)
                pg.draw.circle(tower_range_img, HALF_WHITE, (tower_range, tower_range), tower_range)
            tower_img = tower["image"].copy().convert_alpha()
            validity = self.map.is_valid_tower_tile(tower_tile[0], tower_tile[1])

            if validity == 1:
                tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
            elif validity == -1:
                result = True

                if self.node_is_in_path[tower_tile[0]][tower_tile[1]]:
                    self.map.change_node(tower_tile[0], tower_tile[1], 1)
                    self.pathfinder.clear_nodes(self.map.get_map())
                    for start in self.start_data:
                        path = self.pathfinder.astar(((tile_from_xcoords(start.x, self.map.tilesize),
                                                       tile_from_xcoords(start.y, self.map.tilesize)), 0),
                                                     self.goals, False)

                        if not path:
                            result = False
                            break
                    self.map.change_node(tower_tile[0], tower_tile[1], 0)
                    self.pathfinder.clear_nodes(self.map.get_map())
                            
                if result:
                    tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
                    self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 1)
                else:
                    tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                    tower_range_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                    self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 0)
            else:
                tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                tower_range_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)

            tower_pos = tower_img.get_rect(topleft = towerxy)
            tower_range_pos = tower_range_img.get_rect(center=tower_pos.center)
            self.blit(self.camera.apply_image(tower_range_img), self.camera.apply_rect(tower_range_pos))
            self.blit(self.camera.apply_image(tower_img), self.camera.apply_rect(tower_pos))

    def get_lives(self):
        return self.lives

    def get_cause_of_death(self):
        return self.cause_of_death

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.ui.rect.collidepoint(event.pos):
                    self.ui.set_active(not self.ui.active)
                    return -1

                elif self.ui.active:
                    result = self.ui.event((event.pos[0] - self.ui_pos[0], event.pos[1] - self.ui_pos[1]))
                    if isinstance(result, str):
                        if result == "start_wave":
                            self.start_next_wave()
                            return -1

                        tower_coords = tile_from_xcoords(self.ui.tower.rect.x, self.map.tilesize), tile_from_xcoords(self.ui.tower.rect.y, self.map.tilesize)

                        if result == "sell":
                            tower_dat = self.map.remove_tower(tower_coords[0], tower_coords[1])
                            self.pathfinder.clear_nodes(self.map.get_map())
                            for start in self.start_data:
                                for x in range(tile_from_xcoords(start.width, self.map.tilesize)):
                                    for y in range(tile_from_xcoords(start.height, self.map.tilesize)):
                                        self.map.set_valid_tower_tile(tile_from_xcoords(start.x, self.map.tilesize) + x,
                                                                      tile_from_xcoords(start.y, self.map.tilesize) + y,
                                                                      0)
                            self.make_stripped_path_wrapper()
                            self.draw_tower_bases_wrapper()
                            for enemy in self.enemies:
                                enemy.recreate_path()
                            for stage in range(tower_dat[1] + 1):
                                self.protein += round(TOWER_DATA[tower_dat[0]]["stages"][stage]["upgrade_cost"] / 2)
                            BUY_SFX.play()
                            self.ui.deselect_tower()

                        elif result == "upgrade":
                            if self.protein >= TOWER_DATA[self.ui.tower.name]["stages"][self.ui.tower.stage]["upgrade_cost"]:
                                self.map.upgrade_tower(tower_coords[0], tower_coords[1])
                                self.draw_tower_bases(self)
                                BUY_SFX.play()
                                self.ui.get_ui()
                        return -1

                    elif result > -1:
                        if self.protein < TOWER_DATA[self.available_towers[result]]["stages"][0]["upgrade_cost"]:
                            self.current_tower = None
                        else:
                            self.current_tower = self.available_towers[result]
                        return -1

                    elif result == -1:
                        self.current_tower = None
                        self.ui.deselect_tower()
                        return -1

                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                if self.current_tower == None:
                    self.ui.select_tower(x_coord, y_coord)
                    return -1

                if self.protein < TOWER_DATA[self.current_tower]["stages"][0]["upgrade_cost"]:
                    return -1

                if self.map.is_valid_tower_tile(x_coord, y_coord) == 0 or \
                        self.map.change_node(x_coord, y_coord, 1) == False:
                    self.current_tower = None
                    return -1

                self.pathfinder.clear_nodes(self.map.get_map())

                for start in self.start_data:
                    path = self.pathfinder.astar(((tile_from_xcoords(start.x, self.map.tilesize),
                                                   tile_from_xcoords(start.y, self.map.tilesize)), 0),
                                                 self.goals, False)
                    if path == False:
                        self.map.change_node(x_coord, y_coord, 0)
                        self.pathfinder.clear_nodes(self.map.get_map())
                        return -1

                new_tower = Tower(
                    game=self,
                    x=round_to_tilesize(pos[0], self.map.tilesize),
                    y=round_to_tilesize(pos[1], self.map.tilesize),
                    name=self.current_tower)
                self.map.add_tower(x_coord, y_coord, new_tower)
                for start in self.start_data:
                    for x in range(tile_from_xcoords(start.width, self.map.tilesize)):
                        for y in range(tile_from_xcoords(start.height, self.map.tilesize)):
                            self.map.set_valid_tower_tile(tile_from_xcoords(start.x, self.map.tilesize) + x,
                                                          tile_from_xcoords(start.y, self.map.tilesize) + y, 0)
                self.protein -= TOWER_DATA[self.current_tower]["stages"][0]["upgrade_cost"]
                self.current_tower = None

                BUY_SFX.play()
                self.make_stripped_path_wrapper()
                self.draw_tower_bases_wrapper()
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 4:
                self.camera.zoom(ZOOM_AMT_GAME)

            elif event.button == 5:
                self.camera.zoom(-ZOOM_AMT_GAME)

        elif (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return "pause"
        
        elif event == self.game_done_event:
            return "game_over"
        
        return -1
    
class Start():
    def __init__(self, game, start, enemy_type, enemy_count, spawn_delay, spawn_rate):
        self.clock = game.clock
        self.game = game
        self.start = start
        self.rect = game.start_data[start]
        
        self.enemy_type = enemy_type
        self.enemy_count = enemy_count
        if self.enemy_count == -1:
            self.infinity = True
        else:
            self.infinity = False
        self.spawn_delay = spawn_delay
        self.spawn_rate = spawn_rate
        
        self.time_passed = 0
        self.next_spawn = self.spawn_delay * 1000
        
        self.done_spawning = False
        self.start_spawning = False

    def update(self):
        if self.start_spawning:
            self.time_passed += self.clock.get_time()
            
        if (self.time_passed >= self.next_spawn and (self.infinity or self.enemy_count > 0)):
            self.game.enemies.add(Enemy(
                game = self.game,
                x = self.rect.x + random.randrange(1, self.rect.w - ENEMY_DATA[self.enemy_type]["image"].get_width()),
                y = self.rect.y + random.randrange(1, self.rect.h - ENEMY_DATA[self.enemy_type]["image"].get_height()),
                name = self.enemy_type))
            self.next_spawn = self.spawn_rate * 1000
            self.time_passed = 0
            self.enemy_count -= 1
            
            if self.enemy_count == 0:
                self.done_spawning = True
    
    def is_done_spawning(self):
        return self.done_spawning
    
    def enable_spawning(self):
        self.start_spawning = True
    
    def get_rect(self):
        return self.rect

class Goal(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.game = game
        self.groups = game.goals
        super().__init__(self.groups)
        self.rect = pg.Rect(x, y, w, h)

    def get_nodes(self):
        return [((tile_from_xcoords(self.rect.x, self.game.map.tilesize) + x, tile_from_xcoords(self.rect.y, self.game.map.tilesize) + y), 0) for x in range(tile_from_xcoords(self.rect.width, self.game.map.tilesize)) for y in range(tile_from_xcoords(self.rect.height, self.game.map.tilesize))]

    def get_node(self):
        return ((round(self.rect.x / self.game.map.tilesize), round(self.rect.y / self.game.map.tilesize)), 0)

