import sys
import json
import textwrap

from pathfinding import *
from ui import *
from sprites import *
from tilemap import *
from towers import *
from game_stop import *

class Main:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.key.set_repeat(500, 100)
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.menu = Menu(self.screen)
        self.playing = False
        self.started_game = False
        self.game_surf = None # only used to draw static game screen when fading into game_stop screens
        
    def run_pregame(self):
        while not self.started_game:
            self.events()
            self.update()
            self.draw()

    def run_game(self):
        self.game_stop = None
        
        while self.playing:
            self.events()
            self.update()
            self.draw()

        while not self.playing and self.started_game:
            self.events()
            self.draw()

    def update(self):
        if not self.started_game:
            self.menu.update()

        elif self.game.update() == False:
            self.playing = False
        
    def draw(self):
        self.clock.tick(FPS)
        pg.display.set_caption("FPS: {:.2f}".format(self.clock.get_fps()))
        
        if not self.started_game:
            self.menu.draw()
            
        elif self.playing:
            self.game.draw(self.screen)
        
        else:
            if self.game_surf == None:
                self.game_surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.game.draw(self.game_surf)
                self.game.draw_tower_bases(self.game_surf)
                
            if self.game_stop == None:
                if self.game.paused:
                    self.game_stop = Pause()
                else:
                    self.game_stop = GameOver(self.game.lives <= 0, self.game.get_cause_of_death())
                
            if self.game_stop.is_done_fading():
                self.game_stop.draw()
                self.screen.blit(self.game_stop, (0, 0))
            else:
                self.game_stop.draw()
                self.screen.blit(self.game_surf, (0, 0))
                self.screen.blit(self.game_stop, (0, 0))
            
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            elif not self.started_game:
                level = self.menu.event(event)
                if (level != -1):
                    self.game = Game(self.screen, level)
                    self.game.new()
                    self.started_game = True
                    self.playing = True

            else:
                if self.playing:
                    self.game.event(event)

                else:
                    if self.game_stop.can_register_clicks():
                        result = self.game_stop.event(event)
                        
                        if result == "restart":
                            self.playing = True
                            self.game.new()
                            self.game_surf = None
                        elif result == "back to level select":
                            self.started_game = False
                            self.game_surf = None
                        elif result == "resume":
                            self.playing = True
                            self.game_surf = None
                            self.game.resume()

    def quit(self):
        pg.quit()
        sys.exit()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)
        self.started = False
        self.level_button_rect = LEVEL_BUTTON_IMG.get_rect()
        self.level_buttons = [pg.Rect((20, 120), self.level_button_rect.size), pg.Rect((160, 120), self.level_button_rect.size), pg.Rect((300, 120), self.level_button_rect.size)]
        self.level_descs = [None for i in range(len(LEVEL_DATA))]
        self.over_level = -1

    def update(self):
        self.update_level()

    def draw(self):
        self.screen.fill((0, 0, 0))

        if not self.started:
            self.screen.blit(self.camera.apply_image(START_SCREEN_IMG), self.camera.apply_rect(pg.Rect(0, 0, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)))
            return

        lives_font = pg.font.Font(None, LEVEL_BUTTON_IMG.get_rect().w)
        level_text = lives_font.render("Levels", 1, WHITE)
        self.screen.blit(self.camera.apply_image(level_text), self.camera.apply_tuple((START_SCREEN_IMG.get_rect().w / 2 - level_text.get_rect().center[0], 75 - level_text.get_rect().center[1])))

        for i, button in enumerate(self.level_buttons):
            self.screen.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(button))
            lives_text = lives_font.render(str(i + 1), 1, WHITE)
            self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple((button.center[0] - lives_text.get_rect().center[0], button.center[1] - lives_text.get_rect().center[1])))

        if self.over_level != -1:
            if self.level_descs[self.over_level] == None:
                self.get_level_info(self.over_level)
            if self.level_buttons[self.over_level].centerx < self.screen.get_width() / 2:
                self.screen.blit(self.camera.apply_image(self.level_descs[self.over_level]), self.camera.apply_tuple(self.level_buttons[self.over_level].topright))
            else:
                self.screen.blit(self.camera.apply_image(self.level_descs[self.over_level]), self.camera.apply_rect(self.level_descs[self.over_level].get_rect(topright = self.level_buttons[self.over_level].topleft)))

    def get_level_info(self, level):
        height = MENU_OFFSET

        level_data = LEVEL_DATA[level]
        title_font = pg.font.Font(None, MENU_TEXT_SIZE * 2)
        texts = []
        title_text = title_font.render(level_data["title"], 1, WHITE)
        texts.append(title_text)
        height += title_text.get_height() + MENU_OFFSET

        description_font = pg.font.Font(None, MENU_TEXT_SIZE)
        text = textwrap.fill(level_data["description"], 30 - round(MENU_TEXT_SIZE / 30)) # No idea how to really calculate this.
        counter = 0
        for part in text.split('\n'):
            rendered_text = description_font.render(part, 1, WHITE)
            texts.append(rendered_text)
            height += rendered_text.get_height() + MENU_OFFSET
            counter += 1

        if level_data["difficulty"] == 0:
            difficulty_text = description_font.render("Easy", 1, GREEN)
        elif level_data["difficulty"] == 1:
            difficulty_text = description_font.render("Medium", 1, YELLOW)
        elif level_data["difficulty"] == 2:
            difficulty_text = description_font.render("Hard", 1, ORANGE)
        elif level_data["difficulty"] == 3:
            difficulty_text = description_font.render("Very Hard", 1, RED)
        elif level_data["difficulty"] == 4:
            difficulty_text = description_font.render("Extreme", 1, MAROON)
        texts.append(difficulty_text)
        height += difficulty_text.get_height() + MENU_OFFSET

        waves_text = description_font.render("{} Waves".format(len(level_data["waves"])), 1, WHITE)
        texts.append(waves_text)
        height += waves_text.get_height() + MENU_OFFSET

        enemy_surf = pg.Surface((title_text.get_size()[0] + MENU_OFFSET * 2, MENU_TEXT_SIZE))
        enemy_surf.fill(DARKGREY)
        for i, enemy in enumerate(level_data["enemies"]):
            enemy_image = pg.transform.scale(ENEMY_DATA[enemy]["image"], (MENU_TEXT_SIZE, MENU_TEXT_SIZE))
            enemy_surf.blit(enemy_image, (i * (MENU_TEXT_SIZE + MENU_OFFSET), 0))

        texts.append(enemy_surf)
        height += enemy_surf.get_height()

        level_surf = pg.Surface((title_text.get_width() + MENU_OFFSET * 2, height + MENU_OFFSET))
        level_surf.fill(DARKGREY)
        temp_height = MENU_OFFSET
        for text in texts:
            level_surf.blit(text, (MENU_OFFSET, temp_height))
            temp_height += text.get_height() + MENU_OFFSET

        self.level_descs[level] = level_surf


    def update_level(self):
        mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
        for i, button in enumerate(self.level_buttons):
            if button.collidepoint(mouse_pos):
                self.over_level = i
                return
        self.over_level = -1

    def event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and not self.started:
                self.started = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.over_level

        return -1

class Game:
    def __init__(self, screen, level):
        self.screen = screen
        self.level = level # to be used when more levels are added
        
        self.starts = []
        self.start_data = None
        
        self.map = TiledMap(path.join(MAP_FOLDER, "map{}.tmx".format(self.level)))
        self.load_data()
        self.load_level_data()

    def load_data(self):
        self.map_img = self.map.make_map()
        self.map_objects = self.map.make_objects()
        self.map_rect = self.map_img.get_rect()
        
    def load_level_data(self):
        self.level_data = LEVEL_DATA[self.level]
        self.max_wave = len(self.level_data["waves"])

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goal_sprites = pg.sprite.Group()

        self.available_towers = ["t_cell", "b_cell"]
        self.current_tower = None
        self.protein = PROTEIN
        self.lives = LIVES
        
        self.wave = 0 # only updated at the end of new_wave()
        self.paused = False
        self.cause_of_death = "IB"
        self.start_data = []
        self.map.clear_map()
        self.goals = []
        self.buy_sound = pg.mixer.Sound(AUDIO_BUY_PATH)

        width = round(self.map.width / self.map.tilesize)
        height = round(self.map.height / self.map.tilesize)
        arteries = [[1 for row in range(height)] for col in range(width)]
        veins = [[1 for row in range(height)] for col in range(width)]
        artery_entrances = [[1 for row in range(height)] for col in range(width)]
        vein_entrances = [[1 for row in range(height)] for col in range(width)]

        for tile_object in self.map.tmxdata.objects:
            if "start" in tile_object.name:
                self.start_data.insert(int(tile_object.name[5:]), pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height))
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        self.map.set_valid_tower_tile(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                     tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                     0) # make start tile a wall so you can't place a tower on it
                                        # this does not affect the path finding algo
            if tile_object.name == "goal":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        goal = Goal(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                        self.goals.append(((round(goal.rect.x / self.map.tilesize) + i, round(goal.rect.y / self.map.tilesize) + j), 0))
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "artery":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        arteries[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "vein":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        veins[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "artery_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        artery_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0
            elif tile_object.name == "vein_entrance":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        vein_entrances[tile_from_xcoords(tile_object.x, self.map.tilesize) + i][tile_from_xcoords(tile_object.y, self.map.tilesize) + j] = 0

        self.new_wave()
        self.pathfinder = Pathfinder(arteries, artery_entrances, veins, vein_entrances)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.pathfinder.clear_nodes(self.map.get_map())
        self.path = self.pathfinder.astar(((int(self.starts[0].rect.x / self.map.tilesize), int(self.starts[0].rect.y / self.map.tilesize)), 0), self.goals)
        self.make_stripped_path()
        self.draw_tower_bases(self.screen)
        self.ui = UI(self, 200, 10)
        
    def resume(self):
        self.paused = False
        
        for enemy in self.enemies:
            enemy.update_last_move()
        for start in self.starts:
            start.resume_spawn_timer()

    def update(self):
        # update portion of the game loop
        if (self.lives <= 0):
            return False
        
        if self.paused:
            for start in self.starts:
                start.pause_spawn_timer()
            return False
        
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()
        self.ui.update()
        
        if self.current_wave_done():
            if self.wave < self.max_wave:
                self.new_wave()
            elif len(self.enemies) == 0:
                return False
        
    def current_wave_done(self):
        for start in self.starts:
            if not start.is_done_spawning():
                return False
        return True
    
    def new_wave(self):
        self.starts.clear()
        
        wave_data = self.level_data["waves"][self.wave]
                
        for i in range(len(wave_data["enemy_type"])):
            self.starts.append(Start(self, wave_data["start"][i], wave_data["enemy_type"][i], wave_data["enemy_count"][i], wave_data["spawn_delay"][i], wave_data["spawn_rate"][i]))
            
        self.wave += 1

#     def draw_grid(self):
#         for x in range(0, self.map.width, self.map.tilesize):
#             pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, self.map.height))
#         for y in range(0, self.map.height, self.map.tilesize):
#             pg.draw.line(self.screen, LIGHTGREY, (0, y), (self.map.width, y))

    def draw(self, surface):
        surface.fill((0, 0, 0))

        surface.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))

        for start in self.starts:
            pg.draw.rect(surface, GREEN, self.camera.apply_rect(start.rect))
        for goal in self.goal_sprites:
            pg.draw.rect(surface, GREEN, self.camera.apply_rect(goal.rect))

        surface.blit(self.camera.apply_image(self.path_surf), self.camera.apply_rect(self.path_surf.get_rect()))
        surface.blit(self.camera.apply_image(self.tower_bases_surf), self.camera.apply_rect(self.tower_bases_surf.get_rect()))

        for tower in self.towers:
            rotated_image = pg.transform.rotate(tower.gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            surface.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))

        for enemy in self.enemies:
            surface.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            pg.draw.rect(surface, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for projectile in self.projectiles:
            surface.blit(self.camera.apply_image(projectile.image), self.camera.apply_rect(projectile.rect))

        if self.current_tower != None:
            self.draw_tower_preview(surface)

        surface.blit(self.camera.apply_image(self.map_objects), self.camera.apply_rect(self.map_rect))

        ui_pos = (surface.get_size()[0] - self.ui.offset, self.ui.offset)
        if self.ui.active:
            ui = self.ui.ui
            ui_rect = ui.get_rect(topright = ui_pos)
            surface.blit(ui, ui_rect)
            surface.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright = ui_rect.topleft))
        else:
            surface.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright = ui_pos))
            
        return surface
    
    def make_stripped_path(self):
        self.path_surf = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        self.path_surf.fill((0, 0, 0, 0))

        done = []
        for start in self.starts:
            if start.start in done:
                continue

            xpos = tile_from_xcoords(start.rect.x, self.map.tilesize)
            ypos = tile_from_xcoords(start.rect.y, self.map.tilesize)
            for x in range(tile_from_xcoords(start.rect.w, self.map.tilesize)):
                for y in range(tile_from_xcoords(start.rect.h, self.map.tilesize)):
                    path = self.pathfinder.astar(((xpos + x, ypos + y), 0), self.goals)
                    self.stripped_path = []
                    for i, node in enumerate(path):
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

                            if diff_x_before == 0 and diff_x_after == 0: # up <--> down
                                image = PATH_VERTICAL_IMG
                            elif diff_y_before == 0 and diff_y_after == 0: # left <--> right
                                image = PATH_HORIZONTAL_IMG
                            elif (diff_x_before == 1 and diff_y_after == 1) or (diff_y_before == 1 and diff_x_after == 1): # right <--> down
                                image = PATH_CORNER1_IMG
                            elif (diff_x_before == -1 and diff_y_after == 1) or (diff_y_before == 1 and diff_x_after == -1): # left <--> down
                                image = PATH_CORNER2_IMG
                            elif (diff_x_before == 1 and diff_y_after == -1) or (diff_y_before == -1 and diff_x_after == 1): # right <--> up
                                image = PATH_CORNER3_IMG
                            elif (diff_x_before == -1 and diff_y_after == -1) or (diff_y_before == -1 and diff_x_after == -1): # left <--> up
                                image = PATH_CORNER4_IMG
                            else:
                                print("PATH DRAWING ERROR") # this should never occur

                            self.path_surf.blit(image, pg.Rect(node[0] * self.map.tilesize, node[1] * self.map.tilesize, self.map.tilesize, self.map.tilesize))

    def draw_tower_bases(self, surface):
        self.tower_bases_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.tower_bases_surf.fill((0, 0, 0, 0))
        for tower in self.towers:
            self.tower_bases_surf.blit(tower.base_image, tower.rect)

    def draw_tower_preview(self, surface):
        mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
        towerxy = (round_to_tilesize(mouse_pos[0], self.map.tilesize), round_to_tilesize(mouse_pos[1], self.map.tilesize))
        tower_tile = (tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize))
        pos = self.map.get_node(tower_tile[0], tower_tile[1])

        if pos != -1:
            tower_img = self.camera.apply_image(TOWER_DATA[self.current_tower][0]["image"].copy())
            validity = self.map.is_valid_tower_tile(tower_tile[0], tower_tile[1])

            if validity == 1:
                tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
            elif validity == -1:
                self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize), 1)
                self.pathfinder.clear_nodes(self.map.get_map())
                result = self.pathfinder.astar(((tile_from_xcoords(self.starts[0].rect.x, self.map.tilesize),
                                            tile_from_xcoords(self.starts[0].rect.y, self.map.tilesize)), 0),
                                self.goals)
                self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize), 0)
                self.pathfinder.clear_nodes(self.map.get_map())

                if result != False:
                    tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
                    self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 1)
                else:
                    tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                    self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 0)
            else:
                tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)

            tower_pos = pg.Rect(towerxy, TOWER_DATA[self.current_tower][0]["base_image"].get_size())
            surface.blit(tower_img, self.camera.apply_rect(tower_pos))
        
    def get_lives(self):
        return self.lives
    
    def get_cause_of_death(self):
        return self.cause_of_death

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.ui.rect.collidepoint(event.pos):
                    self.ui.set_active(not self.ui.active)
                    return

                elif self.ui.active:
                    for i, tower_rect in enumerate(self.ui.tower_rects):
                        if (self.protein < TOWER_DATA[self.available_towers[i]][0]["upgrade_cost"]):
                            continue
                        temp_rect = tower_rect.copy()
                        temp_rect.x += self.screen.get_size()[0] - self.ui.width
                        if temp_rect.collidepoint(event.pos):
                            self.current_tower = self.available_towers[i]
                            return

                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                if self.map.get_node(x_coord, y_coord) == 1:
                    self.map.upgrade_tower(x_coord, y_coord) # don't need to upgrade tower if clicking on empty space
                    return

                if self.map.is_valid_tower_tile(x_coord, y_coord) == 0:
                    return

                if self.current_tower == None:
                    return

                if self.map.change_node(x_coord, y_coord, 1) == False:
                    return


                self.pathfinder.clear_nodes(self.map.get_map())

                for start in self.starts:
                    path = self.pathfinder.astar(((tile_from_xcoords(self.starts[0].rect.x, self.map.tilesize),
                                        tile_from_xcoords(self.starts[0].rect.y, self.map.tilesize)), 0),
                            self.goals)
                    if path == False:
                        self.map.change_node(x_coord, y_coord, 0)
                        self.pathfinder.clear_nodes(self.map.get_map())
                        return

                new_tower = Tower(
                    game = self,
                    x = round_to_tilesize(pos[0], self.map.tilesize),
                    y = round_to_tilesize(pos[1], self.map.tilesize),
                    name = self.current_tower)
                self.map.add_tower(x_coord, y_coord, new_tower)
                self.protein -= TOWER_DATA[self.current_tower][0]["upgrade_cost"]
                self.current_tower = None

                self.buy_sound.play()
                self.make_stripped_path()
                self.draw_tower_bases(self.screen)
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 3:
                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                self.map.remove_tower(x_coord, y_coord)
                self.pathfinder.clear_nodes(self.map.get_map())
                self.make_stripped_path()
                self.draw_tower_bases()
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 4:
                self.camera.zoom(0.05, event.pos)

            elif event.button == 5:
                self.camera.zoom(-0.05, event.pos)
                
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.paused = True

# create the game object
g = Main()
while True:
    g.run_pregame()
    g.run_game()
