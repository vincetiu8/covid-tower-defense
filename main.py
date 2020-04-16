import sys
import json

from ui import *
from sprites import *
from tilemap import *
from towers import *

class Main:
    def __init__(self):
        pg.init()
        pg.key.set_repeat(500, 100)
        self.menu = Menu(pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)))
        self.playing = False
        self.started_game = False
        while not self.started_game:
            self.events()
            self.draw()

    def run_game(self): 
        while self.playing:
            self.events()
            self.update()
            self.draw()

        while not self.playing:
            self.events()

    def update(self):
        if self.game.update() == False:
            self.playing = False
        
    def draw(self):
        if not self.started_game:
            self.menu.draw()
            
        elif self.playing:
            self.game.draw()
            
        else:
            self.game.draw() # updates game_screen one last time
            self.game.draw_game_over(self.game.get_lives() == 0)
            
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.quit()

            elif not self.started_game:
                level = self.menu.event(event)
                if (level != False):
                    self.game = Game(pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)), level)
                    self.game.new()
                    self.started_game = True
                    self.playing = True

            else:
                if self.playing:
                    self.game.event(event)

                else:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_r:
                            self.playing = True
                            self.game.playing = True
                            self.game.new()

    def quit(self):
        pg.quit()
        sys.exit()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)
        self.started = False
        self.level_buttons = [pg.Rect(20, 120, LEVEL_BUTTON_IMG.get_rect().w, LEVEL_BUTTON_IMG.get_rect().h)]

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

    def event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and not self.started:
                self.started = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            for i, button in enumerate(self.level_buttons):
                if button.collidepoint(self.camera.correct_mouse(mouse_pos)):
                    return i + 1

        return False


class Game:
    def __init__(self, screen, level):
        self.screen = screen
        self.level = level # to be used when more levels are added
        
        self.starts = []
        self.start_data = None
        self.clock = pg.time.Clock()
        
        self.map = TiledMap(path.join(MAP_FOLDER, "map{}.tmx".format(self.level)))
        self.load_data()
        self.load_level_data()

    def load_data(self):
        self.map_img = self.map.make_map()
        self.map_objects = self.map.make_objects()
        self.map_rect = self.map_img.get_rect()
        
    def load_level_data(self):
        self.level_data = None
        
        with open(SAMPLE_LEVEL_DATA, "r") as data_file:
            self.level_data = json.load(data_file)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        
        self.protein = PROTEIN
        self.lives = LIVES
        
        self.wave = 0 # only updated at the end of new_wave()
        
        self.reset_map()
        
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "start":
                self.start_data = {"x": tile_object.x, "y": tile_object.y, "w": tile_object.width, "h": tile_object.height}
                self.new_wave()
            if tile_object.name == "goal":
                self.goal = Goal(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.path = astar(self.map.get_map(), (int(self.starts[0].x / self.map.tilesize), int(self.starts[0].y / self.map.tilesize)),
                          (int(self.goal.x / self.map.tilesize), int(self.goal.y / self.map.tilesize)))

        self.ui = UI(self, 200, 10)

    def update(self):
        # update portion of the game loop
        if (self.lives <= 0):
            return False
        
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()
        self.ui.update()
        
        if self.current_wave_done():
            if self.wave < len(self.level_data):
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
        
        wave_data = self.level_data[self.wave]
                
        for i in range(len(wave_data["enemy_type"])):
            self.starts.append(Start(self, self.start_data["x"], self.start_data["y"], self.start_data["w"], self.start_data["h"], wave_data["enemy_type"][i], wave_data["enemy_count"][i], wave_data["spawn_delay"][i], wave_data["spawn_rate"][i]))
            
        self.wave += 1

#     def draw_grid(self):
#         for x in range(0, self.map.width, self.map.tilesize):
#             pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, self.map.height))
#         for y in range(0, self.map.height, self.map.tilesize):
#             pg.draw.line(self.screen, LIGHTGREY, (0, y), (self.map.width, y))

    def draw(self):
        pg.display.set_caption("FPS: {:.2f}  Protein: {}  Wave: {}".format(self.clock.get_fps(), self.protein, self.wave))
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))
        applied_goal_rect = self.camera.apply_rect(self.goal.rect)

        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.starts[0].rect))
        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.goal.rect))

        # draws # of lives left on goal
        lives_font = pg.font.Font(None, self.map.tilesize)
        lives_text = lives_font.render(str(self.lives), 1, BLACK)
        self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple((self.goal.rect.left + self.map.tilesize // 4,
                                      self.goal.rect.top + self.map.tilesize // 4)))
        
        self.draw_path()

        for tower in self.towers:
            base_image = tower.base_images[tower.stage]
            gun_image = tower.gun_images[tower.stage]
            
            self.screen.blit(self.camera.apply_image(base_image), self.camera.apply_rect(tower.rect))
            rotated_image = pg.transform.rotate(gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            self.screen.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))

        for enemy in self.enemies:
            self.screen.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for projectile in self.projectiles:
            pg.draw.rect(self.screen, LIGHTGREY, self.camera.apply_rect(projectile.rect))

        if self.protein >= BUY_COST:
            mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
            towerxy = (round_to_tilesize(mouse_pos[0], self.map.tilesize), round_to_tilesize(mouse_pos[1], self.map.tilesize))
            tower_tile = (tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize))
            pos = self.map.get_node(tower_tile[0], tower_tile[1])

            if pos != -1:
                tower_img = self.camera.apply_image(ANTIBODY_BASE_IMGS[0]).copy()
                tower_img.blit(self.camera.apply_image(ANTIBODY_GUN_IMGS[0]), (tower_img.get_rect()[0] / 2, tower_img.get_rect()[1] / 2))
                validity = self.map.is_valid_tower_tile(tower_tile[0], tower_tile[1])
                
                if validity == 1:
                    tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
                elif validity == -1:
                    self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize), 1)
                    result = astar(self.map.get_map(), (tile_from_xcoords(self.starts[0].x, self.map.tilesize),
                                                tile_from_xcoords(self.starts[0].y, self.map.tilesize)),
                                    (tile_from_xcoords(self.goal.x, self.map.tilesize),
                                      tile_from_xcoords(self.goal.y, self.map.tilesize)))
                    self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize), 0)
                    
                    if result != False:
                        tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
                        self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 1)
                    else:
                        tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                        self.map.set_valid_tower_tile(tower_tile[0], tower_tile[1], 0)
                else:
                    tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)

                tower_pos = pg.Rect(towerxy, ANTIBODY_BASE_IMGS[0].get_size())
                self.screen.blit(tower_img, self.camera.apply_rect(tower_pos))

        self.screen.blit(self.map_objects, self.camera.apply_rect(self.map_rect))

        ui_pos = (self.screen.get_size()[0] - self.ui.offset, self.ui.offset)
        if self.ui.active:
            ui = self.ui.ui
            ui_rect = ui.get_rect(topright = ui_pos)
            self.screen.blit(ui, ui_rect)
            self.screen.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright = ui_rect.topleft))

        else:
            self.screen.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright = ui_pos))
        
    def draw_path(self):
        for i, node in enumerate(self.path):
            if (i > 0 and i < len(self.path) - 1):
                image = None
                diff_x_before = self.path[i - 1][0] - node[0]
                diff_x_after = self.path[i + 1][0] - node[0]
                diff_y_before = self.path[i - 1][1] - node[1]
                diff_y_after = self.path[i + 1][1] - node[1]
                
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
                    
                self.screen.blit(self.camera.apply_image(image), self.camera.apply_rect(
                    pg.Rect(node[0] * self.map.tilesize, node[1] * self.map.tilesize, self.map.tilesize, self.map.tilesize)))

    def draw_game_over(self, lost_game):
        game_over_font_1 = pg.font.Font(None, 140)
        game_over_font_2 = pg.font.Font(None, 60)
        
        text = "YOU WON!"
        if lost_game:
            text = "GAME OVER"
            
        game_over_text_1 = game_over_font_1.render(text, 1, WHITE)
        game_over_text_2 = game_over_font_2.render("Press R to Restart", 1, WHITE)

        self.screen.blit(game_over_text_1, (40, 40)) # hardcoding coords lol
        self.screen.blit(game_over_text_2, (40, 140))

        pg.display.flip()

    def reset_map(self):
        self.map.clear_map()
        
    def get_lives(self):
        return self.lives

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.ui.rect.collidepoint(event.pos):
                    self.ui.set_active(not self.ui.active)
                    return

                tile_map = self.map.get_map()
                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)
                
                if self.map.get_node(x_coord, y_coord) != 0:
                    self.map.upgrade_tower(x_coord, y_coord) # don't need to upgrade tower if clicking on empty space
                    return
                    
                if self.protein < BUY_COST:
                    return
                
                if self.map.change_node(x_coord, y_coord, 1) == False:
                    return
                
                path = astar(tile_map, (tile_from_xcoords(self.starts[0].x, self.map.tilesize),
                                        tile_from_xcoords(self.starts[0].y, self.map.tilesize)),
                            (tile_from_xcoords(self.goal.x, self.map.tilesize),
                                tile_from_xcoords(self.goal.y, self.map.tilesize)))
                                    
                if path != False:
                    self.path = path
                    
                    new_tower = Tower(
                        game = self,
                        x = round_to_tilesize(pos[0], self.map.tilesize),
                        y = round_to_tilesize(pos[1], self.map.tilesize),
                        base_images = ANTIBODY_BASE_IMGS,
                        gun_images = ANTIBODY_GUN_IMGS,
                        bullet_spawn_speed = 0.2,
                        bullet_speed = 25,
                        bullet_size = 8,
                        damage = [(i + 1) for i in range(MAX_STAGE + 1)],
                        range = 200,
                        upgrade_cost = 5,
                        max_stage = MAX_STAGE)
                    self.map.add_tower(x_coord, y_coord, new_tower)
                    self.protein -= BUY_COST
                    
                    for enemy in self.enemies:
                        enemy.recreate_path()
                else:  # reverts tile map to previous state if no enemy path could be found
                    tile_map[x_coord][y_coord] = 0

            elif event.button == 3:
                tile_map = self.map.get_map()
                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                self.map.remove_tower(x_coord, y_coord)
                self.path = astar(tile_map, (tile_from_xcoords(self.starts[0].x, self.map.tilesize),
                                        tile_from_xcoords(self.starts[0].y, self.map.tilesize)),
                            (tile_from_xcoords(self.goal.x, self.map.tilesize),
                              tile_from_xcoords(self.goal.y, self.map.tilesize)))
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 4:
                self.camera.zoom(0.05, event.pos)

            elif event.button == 5:
                self.camera.zoom(-0.05, event.pos)

# create the game object
g = Main()
while True:
    g.run_game()
