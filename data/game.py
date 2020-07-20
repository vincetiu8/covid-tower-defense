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

skip_to_wave = 16   # TODO: Remove this dev option
                    # Change this to change which wave you start on. You'll get all the protein from the previous waves.
                    # Indexing starts at 0 and the wave this is set to is inclusive.
                    # i.e. if the value is set to 15, the game will start at wave 16 (when counting from 1).

class Game(Display):
    def __init__(self, clock):
        super().__init__()
        self.clock = clock

        self.game_done_event = pg.event.Event(pg.USEREVENT)
        
        self.ui_pos = None
        self.key_map = {
            pg.K_1: 0,
            pg.K_2: 1,
            pg.K_3: 2,
            pg.K_4: 3,
            pg.K_5: 4
        }

    def load_data(self):
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def load_level_data(self):
        self.level_data = LEVEL_DATA[self.level]
        self.max_wave = len(self.level_data["waves"][self.difficulty])
        
    def new(self, args):
        self.level, self.difficulty = args[0]
        to_resume = args[1]
        self.available_towers = args[2]
        
        if not to_resume:
            self.new_game()
        else:
            pg.mixer.music.unpause()
    
    def new_game(self):
        self.map = TiledMap(path.join(MAP_FOLDER, "{}.tmx".format(list(BODY_PARTS)[LEVEL_DATA[self.level]["body_part"]])))
        self.load_data()
        self.load_level_data()
        
        # initialize all variables and do all the setup for a new game
        self.new_enemy_box = NewEnemyBox()
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.starts = []

        self.current_tower = None
        self.protein = SAVE_DATA["game_attrs"]["starting_protein"]["value"]
        self.lives = SAVE_DATA["game_attrs"]["lives"]["value"]

        self.wave = -1  # only updated at the start of prepare_next_wave()
        self.in_a_wave = False

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
                        self.map.set_start_tile(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j)  # make start tile a wall so you can't place a tower on it
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
                        if artery_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] == 0:
                            self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                1)
            elif tile_object.name == "vein":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        veins[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
                        if vein_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] == 0:
                            self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                1)
            elif tile_object.name == "artery_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        artery_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
                        if arteries[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] == 0:
                            self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                1)
            elif tile_object.name == "vein_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        vein_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][
                            tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
                        if veins[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] == 0:
                            self.map.change_node(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                1)

        for start in self.start_data:
            for x in range(tile_from_xcoords(start.width, self.map.tilesize)):
                for y in range(tile_from_xcoords(start.height, self.map.tilesize)):
                    self.map.set_valid_tower_tile(tile_from_xcoords(start.x, self.map.tilesize) + x, tile_from_xcoords(start.y, self.map.tilesize) + y, 0)

        self.pathfinder = Pathfinder(
            arteries = arteries,
            artery_entrances = artery_entrances,
            veins = veins,
            vein_entrances = vein_entrances,
            base_map = self.map.get_map())
        
        songs = [MILD_LEVEL_MUSIC, ACUTE_LEVEL_MUSIC, SEVERE_LEVEL_MUSIC]
        pg.mixer.music.set_endevent()
        pg.mixer.music.stop()
        pg.mixer.music.load(songs[self.difficulty][self.level // 11])
        if self.difficulty == 2 and self.level // 11 == 1: # only for late severe levels
            pg.mixer.music.play(0) # have to make the song play 0 times for some reason...
            pg.mixer.music.set_endevent(pg.USEREVENT + 3)
        else:
            pg.mixer.music.play(-1)
        
        self.node_is_in_path = [[]]
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.pathfinder.clear_nodes(self.map.get_map())
        self.textbox = Textbox(self)
        self.ui = UI(self, 10)
        self.prepare_next_text()
        self.draw_tower_bases_wrapper()
        self.make_stripped_path_wrapper()
        self.mouse_pos = (0, 0)
        
        self.calculate_path()

    def update(self):
        if self.new_enemy_box.show:
            self.new_enemy_box.update()

        else:
            # update portion of the game loop
            for start in self.starts:
                start.update()
            self.enemies.update()
            self.towers.update()
            self.projectiles.update()
            self.ui.update()
            self.explosions.update()

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                self.camera.move(25, 0)

            elif keys[pg.K_RIGHT]:
                self.camera.move(-25, 0)

            elif keys[pg.K_UP]:
                self.camera.move(0, 25)

            elif keys[pg.K_DOWN]:
                self.camera.move(0, -25)

            # if self.lives <= 0: TODO: Add this back
            #     pg.event.post(self.game_done_event)

            if self.text:
                if SAVE_DATA["skip_text"]:
                    self.textbox.toggle(False)
                    self.ui.set_next_wave_btn(True)
                    TEXT_SCROLL_SFX.stop()
                else:
                    self.textbox.update()
                return

            if not self.in_a_wave and self.wave > 0:
                self.time_passed += self.clock.get_time()
                if self.time_passed >= WAVE_DELAY * 1000:
                    self.start_next_wave()

            if self.in_a_wave and self.current_wave_done():
                    if self.wave < self.max_wave:
                        self.prepare_next_text()
                    elif len(self.enemies) == 0:
                        pg.event.post(self.game_done_event)

    def current_wave_done(self):
        for start in self.starts:
            if not start.is_done_spawning():
                return False
        return True
    
    def prepare_next_text(self):
        # Wave has text --> text (and the next wave) don't appear until previous wave is all dead
        # Wave has no text --> next wave starts counting down immediately after previous wave is done spawning
        if not SAVE_DATA["skip_text"] and self.level_data["texts"][self.difficulty].get(str(self.wave + 1)) != None:
            if len(self.enemies) == 0:
                self.text = True
                self.texts = self.level_data["texts"][self.difficulty][str(self.wave + 1)].copy()
                self.ui.set_next_wave_btn(False)
                self.textbox.set_text(self.texts[0])
                self.textbox.finish_text()
                self.textbox.yoffset = self.textbox.rect.height
                self.textbox.toggle(True)
        else:
            self.text = False
            self.textbox.enabled = False
            self.prepare_next_wave()

    def prepare_next_wave(self):
        self.wave += 1
        while self.wave < skip_to_wave: # TODO: Remove this dev option
            for i in self.level_data["waves"][self.difficulty][self.wave]:
                self.protein += i["enemy_count"] * ENEMY_DATA[i["enemy_type"]]["protein"]

            self.wave += 1

        if self.wave == self.max_wave:
            return

        self.in_a_wave = False
        self.ui.set_next_wave_btn(True)
        self.ui.generate_next_wave_wrapper()
        self.time_passed = 0

        self.starts.clear()
        for i in self.level_data["waves"][self.difficulty][self.wave]:
            self.starts.append(
                Start(self, i["start"], i["enemy_type"], i["enemy_count"],
                        i["spawn_delay"], i["spawn_rate"]))

        self.make_stripped_path_wrapper()

    def start_next_wave(self):
        self.in_a_wave = True
        self.ui.set_next_wave_btn(False)
        self.ui.generate_header()
        self.ui.generate_next_wave_wrapper()

        for start in self.starts:
            start.enable_spawning()
            if start.enemy_type not in SAVE_DATA["seen_enemies"]:
                SAVE_DATA["seen_enemies"].append(start.enemy_type)
                self.new_enemy_box.show_new_enemy(start.enemy_type)

    def draw(self):
        temp_surf = pg.Surface((self.map_rect.w, self.map_rect.h))

        temp_surf.blit(self.map_img, self.map_rect)

        temp_surf.blit(self.path_surf, (0, 0))

        temp_surf.blit(self.tower_bases_surf, self.tower_bases_surf.get_rect())

        for tower in self.towers:
            if tower.area_of_effect or not tower.rotating:
                continue
            rotated_image = pg.transform.rotate(tower.gun_image, math.degrees(tower.rotation))
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            temp_surf.blit(rotated_image, new_rect)

        for enemy in self.enemies:
            if enemy.image_size > 0:
                temp_surf.blit(enemy.image, enemy.rect)
            hp_surf = enemy.get_hp_surf()
            if hp_surf != None:
                temp_surf.blit(hp_surf, hp_surf.get_rect(center=(enemy.rect.center[0], enemy.rect.center[1] - 15)))

        for projectile in self.projectiles:
            temp_surf.blit(projectile.image, projectile.rect)
        
        self.draw_aoe_sprites(self)
        temp_surf.blit(self.aoe_surf, (0, 0))

        for explosion in self.explosions:
            temp_surf.blit(explosion.get_surf(), (explosion.x, explosion.y))

        if self.current_tower != None:
            self.draw_tower_preview(temp_surf)

        if self.ui.tower != None and not self.ui.tower.area_of_effect:
            tower_range_img = pg.Surface((self.ui.tower.true_range * 2, self.ui.tower.true_range * 2)).convert_alpha()
            tower_range_img.fill(BLANK)
            pg.draw.circle(tower_range_img, HALF_WHITE, (self.ui.tower.true_range, self.ui.tower.true_range), self.ui.tower.true_range)
            temp_surf.blit(tower_range_img, tower_range_img.get_rect(center=self.ui.tower.rect.center))

        self.fill(BLACK)
        self.blit(self.camera.apply_image(temp_surf), self.camera.apply_tuple((0, 0)))

        self.ui_pos = [self.get_size()[0] - self.ui.offset, self.ui.offset]
        if self.ui.active:
            self.ui_pos[0] -= self.ui.width
            ui = self.ui.ui
            ui_rect = ui.get_rect(topleft = self.ui_pos)
            self.blit(ui, ui_rect)
            self.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright = ui_rect.topleft))
        else:
            self.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright = (SCREEN_WIDTH - MENU_OFFSET, MENU_OFFSET)))
        
        if len(self.enemies) == 0 and self.text:
            self.blit(self.textbox, self.textbox.get_rect(bottomleft = (MENU_OFFSET, SCREEN_HEIGHT - MENU_OFFSET + self.textbox.yoffset)))

        if self.new_enemy_box.show:
            self.blit(self.new_enemy_box.get_surf(), self.new_enemy_box.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))

        return self

    def make_stripped_path_wrapper(self):
        self.make_stripped_path(self.map_img)

    def make_stripped_path(self, surface): # used to draw the path for the enemies in the current wave
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
                    index = 0
                    for i, node in enumerate(path):
                        if self.map.is_start_tile(node[0][0], node[0][1]):
                            index = i
                            continue
                            
                        if (i < len(path) - 1):
                            diff_x_after = path[i + 1][0][0] - node[0][0]
                            diff_y_after = path[i + 1][0][1] - node[0][1]
                            if (diff_x_after == 0 and diff_y_after == 0):
                                continue
                        self.stripped_path.append(node[0])

                    self.stripped_path.insert(0, path[index][0])

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
        self.tower_bases_surf = pg.Surface((self.map_img.get_width(), self.map_img.get_height()), pg.SRCALPHA)
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

    def draw_tower_preview(self, temp_surf):
        towerxy = (
            round_to_tilesize(self.mouse_pos[0], self.map.tilesize), round_to_tilesize(self.mouse_pos[1], self.map.tilesize))
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
            temp_surf.blit(tower_range_img, tower_range_pos)
            temp_surf.blit(tower_img, tower_pos)

    def get_lives(self):
        return self.lives

    def get_cause_of_death(self):
        return self.cause_of_death

    def calculate_path(self): 
        paths = []
        valid_path = True
        
        for start in self.start_data:
            xpos = tile_from_xcoords(start.x, self.map.tilesize)
            ypos = tile_from_xcoords(start.y, self.map.tilesize)
            for x in range(tile_from_xcoords(start.w, self.map.tilesize)):
                for y in range(tile_from_xcoords(start.h, self.map.tilesize)):
                    path = self.pathfinder.astar(((xpos + x, ypos + y), 0), self.goals, False)
                    if path == False:
                        valid_path = False
                        break
                    else:
                        paths.append(path)
                        
                if not valid_path:
                    break
            if not valid_path:
                break
        
        # update which nodes in a path
        if valid_path:
            self.node_is_in_path = [[False for i in range(len(self.map.get_map()[0]))] for j in range(len(self.map.get_map()))]
            for path in paths:
                for node in path:
                    if node[1] == 0: # not artery or vein
                        self.node_is_in_path[node[0][0]][node[0][1]] = True
        
        return valid_path

    def sell_tower(self, tower, tower_coords):
        self.map.remove_tower(tower_coords[0], tower_coords[1])
        tower.on_remove()
        tower.kill()
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
        for stage in range(tower.stage + 1):
            self.protein += round(
                TOWER_DATA[tower.name]["stages"][stage]["upgrade_cost"] * (1 + self.difficulty * 0.25) / 2)
        BUY_SFX.play()
        self.ui.generate_header()
        self.ui.deselect_tower()

    def upgrade_tower(self, tower):
        if tower.stage == 2:
            return

        if self.protein >= round(TOWER_DATA[tower.name]["stages"][tower.stage + 1]["upgrade_cost"] * (
                1 + self.difficulty * 0.25)):
            tower.upgrade()
            self.draw_tower_bases(self)
            BUY_SFX.play()
            self.ui.generate_header()
            self.ui.generate_body_wrapper()
        else:
            WRONG_SELECTION_SFX.play()
            
    def select_tower(self, index):
        if self.protein < round(TOWER_DATA[self.available_towers[index]]["stages"][0]["upgrade_cost"] * (1 + self.difficulty * 0.25)):
            WRONG_SELECTION_SFX.play()
            self.current_tower = None
        else:
            BTN_2_SFX.play()
            
            if self.current_tower == self.available_towers[index]:
                self.current_tower = None
            else:
                self.current_tower = self.available_towers[index]

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.new_enemy_box.enabled:
                    self.new_enemy_box.enabled = False
                    self.paused = False

                if self.text:
                    if self.textbox.writing:
                        self.textbox.fast_forward()
                    elif len(self.texts) == 1:
                        self.textbox.toggle(False)
                        self.ui.set_next_wave_btn(True)
                    else:
                        self.texts = self.texts[1:]
                        self.textbox.set_text(self.texts[0])
                    return -1

                if self.ui.rect.collidepoint(event.pos):
                    self.ui.set_active(not self.ui.active)
                    return -1

                elif self.ui.active:
                    result = self.ui.event((event.pos[0] - self.ui_pos[0], event.pos[1] - self.ui_pos[1]))
                    if isinstance(result, str):
                        if result == "start_wave":
                            BTN_2_SFX.play()
                            self.start_next_wave()
                            return -1

                        tower_coords = tile_from_xcoords(self.ui.tower.rect.x, self.map.tilesize), tile_from_xcoords(self.ui.tower.rect.y, self.map.tilesize)

                        if result == "sell":
                            self.sell_tower(self.ui.tower, tower_coords)

                        elif result == "upgrade":
                            self.upgrade_tower(self.ui.tower)

                        elif result == "target":
                            self.ui.tower.targeting_option += 1
                            if self.ui.tower.targeting_option == len(TARGET_OPTIONS):
                                self.ui.tower.targeting_option = 0
                            self.ui.generate_body_wrapper()
                        return -1

                    elif result > -1:
                        self.select_tower(result)
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

                if self.protein < round(TOWER_DATA[self.current_tower]["stages"][0]["upgrade_cost"] * (1 + 0.25 * self.difficulty)):
                    return -1

                if self.map.is_valid_tower_tile(x_coord, y_coord) == 0 or \
                        self.map.change_node(x_coord, y_coord, 1) == False:
                    WRONG_SELECTION_SFX.play()
                    self.current_tower = None
                    return -1

                self.pathfinder.clear_nodes(self.map.get_map())

                if not self.calculate_path():
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
                cost = round(TOWER_DATA[self.current_tower]["stages"][0]["upgrade_cost"] * (1 + self.difficulty * 0.25))
                self.protein -= cost
                if not pg.key.get_pressed()[pg.K_LSHIFT] or self.protein < cost:
                    self.current_tower = None

                BUY_SFX.play()
                self.ui.generate_header()
                self.ui.generate_body_wrapper()

                self.make_stripped_path_wrapper()
                self.draw_tower_bases_wrapper()
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 2 or event.button == 3:
                mouse_pos = self.camera.correct_mouse(event.pos)
                tower_coords = tile_from_coords(mouse_pos[0], self.map.tilesize), tile_from_coords(
                    mouse_pos[1], self.map.tilesize)
                tower = self.map.get_tower(tower_coords[0], tower_coords[1])
                if tower != None:
                    if event.button == 2:
                        self.sell_tower(tower, tower_coords)
                    else:
                        self.upgrade_tower(tower)

            elif event.button == 4:
                self.camera.zoom(ZOOM_AMT_GAME)

            elif event.button == 5:
                self.camera.zoom(-ZOOM_AMT_GAME)

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.mixer.music.pause()
                return "pause"
            elif self.key_map.get(event.key) != None:
                tower_ind = self.key_map[event.key]
                
                if tower_ind < len(self.available_towers):
                    self.select_tower(tower_ind)
                else:
                    WRONG_SELECTION_SFX.play()
                    
                return -1

        elif event.type == pg.MOUSEMOTION:
            self.mouse_pos = self.camera.correct_mouse(event.pos)
        
        elif event == self.game_done_event:
            pg.mixer.music.stop()
            return "game_over"
        
        elif event.type == pg.USEREVENT + 3: # skip the intro part of the late severe song when looping
            pg.mixer.music.load(LATE_SEVERE_MUSIC_LOOP)
            pg.mixer.music.play(-1)
            pg.mixer.music.set_endevent()
        
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
            tilesize = self.game.map.tilesize
            self.game.enemies.add(Enemy(
                game = self.game,
                x = self.rect.x + ENEMY_DATA[self.enemy_type]["image"].get_width() + tilesize * random.randint(0, self.rect.w // tilesize - 1),
                y = self.rect.y + ENEMY_DATA[self.enemy_type]["image"].get_height() + tilesize * random.randint(0, self.rect.h // tilesize - 1),
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

