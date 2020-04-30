from data.tilemap import *
from data.enemies import *
from data.pathfinding import *
from data.ui import *
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
        self.starts = []
        self.game_done_event = pg.event.Event(pg.USEREVENT)

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
        self.map = TiledMap(path.join(MAP_FOLDER, "map{}.tmx".format(self.level)))
        self.load_data()
        self.load_level_data()
        
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goals = pg.sprite.Group()

        self.current_tower = None
        self.protein = PROTEIN
        self.lives = LIVES

        self.wave = 0  # only updated at the end of new_wave()
        self.cause_of_death = "IB"
        self.start_data = []
        self.map.clear_map()
        self.buy_sound = pg.mixer.Sound(AUDIO_BUY_PATH)

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
            if tile_object.name == "artery":
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

        self.new_wave()
        self.pathfinder = Pathfinder(
            arteries = arteries,
            artery_entrances = artery_entrances,
            veins = veins,
            vein_entrances = vein_entrances
        )
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.pathfinder.clear_nodes(self.map.get_map())
        self.make_stripped_path(self)
        self.draw_tower_bases(self)
        self.ui = UI(self, 200, 10)

    def update(self):
        # update portion of the game loop
        for start in self.starts:
            start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()
        self.ui.update()
        
        if self.lives <= 0:
            pg.event.post(self.game_done_event)

        if self.current_wave_done():
            if self.wave < self.max_wave:
                self.new_wave()
            elif len(self.enemies) == 0:
                pg.event.post(self.game_done_event)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.camera.move(25, 0)

        elif keys[pg.K_RIGHT]:
            self.camera.move(-25, 0)

        elif keys[pg.K_UP]:
            self.camera.move(0, 25)

        elif keys[pg.K_DOWN]:
            self.camera.move(0, -25)

    def current_wave_done(self):
        for start in self.starts:
            if not start.is_done_spawning():
                return False
        return True

    def new_wave(self):
        self.starts.clear()

        wave_data = self.level_data["waves"][self.wave]

        for i in range(len(wave_data["enemy_type"])):
            self.starts.append(
                Start(self.clock, self, wave_data["start"][i], wave_data["enemy_type"][i], wave_data["enemy_count"][i],
                      wave_data["spawn_delay"][i], wave_data["spawn_rate"][i]))

        self.wave += 1

    #     def draw_grid(self):
    #         for x in range(0, self.map.width, self.map.tilesize):
    #             pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, self.map.height))
    #         for y in range(0, self.map.height, self.map.tilesize):
    #             pg.draw.line(self.screen, LIGHTGREY, (0, y), (self.map.width, y))

    def draw(self):
        self.fill((0, 0, 0))

        self.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))

        for start in self.starts:
            pg.draw.rect(self, GREEN, self.camera.apply_rect(start.rect))
        for goal in self.goals:
            pg.draw.rect(self, GREEN, self.camera.apply_rect(goal.rect))

        self.blit(self.camera.apply_image(self.path_surf), self.camera.apply_rect(self.path_surf.get_rect()))
        self.blit(self.camera.apply_image(self.tower_bases_surf),
                     self.camera.apply_rect(self.tower_bases_surf.get_rect()))

        for tower in self.towers:
            rotated_image = pg.transform.rotate(tower.gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            self.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))

        for enemy in self.enemies:
            self.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            pg.draw.rect(self, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for projectile in self.projectiles:
            self.blit(self.camera.apply_image(projectile.image), self.camera.apply_rect(projectile.rect))

        if self.current_tower != None:
            self.draw_tower_preview()

        self.blit(self.camera.apply_image(self.map_objects), self.camera.apply_rect(self.map_rect))

        ui_pos = (self.get_size()[0] - self.ui.offset, self.ui.offset)
        if self.ui.active:
            ui = self.ui.ui
            ui_rect = ui.get_rect(topright=ui_pos)
            self.blit(ui, ui_rect)
            self.blit(RIGHT_ARROW_IMG, RIGHT_ARROW_IMG.get_rect(topright=ui_rect.topleft))
        else:
            self.blit(LEFT_ARROW_IMG, LEFT_ARROW_IMG.get_rect(topright=ui_pos))

        return self

    def make_stripped_path(self, surface):
        self.path_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
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

                            self.path_surf.blit(image, pg.Rect(node[0] * self.map.tilesize, node[1] * self.map.tilesize,
                                                               self.map.tilesize, self.map.tilesize))

    def draw_tower_bases(self, surface):
        self.tower_bases_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.tower_bases_surf.fill((0, 0, 0, 0))
        for tower in self.towers:
            self.tower_bases_surf.blit(tower.base_image, tower.rect)

    def draw_tower_preview(self):
        mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
        towerxy = (
        round_to_tilesize(mouse_pos[0], self.map.tilesize), round_to_tilesize(mouse_pos[1], self.map.tilesize))
        tower_tile = (
        tile_from_xcoords(towerxy[0], self.map.tilesize), tile_from_xcoords(towerxy[1], self.map.tilesize))
        pos = self.map.get_node(tower_tile[0], tower_tile[1])

        if pos != -1:
            tower_img = self.camera.apply_image(TOWER_DATA[self.current_tower][0]["image"].copy().convert_alpha())
            validity = self.map.is_valid_tower_tile(tower_tile[0], tower_tile[1])

            if validity == 1:
                tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
            elif validity == -1:
                self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize),
                                     tile_from_xcoords(towerxy[1], self.map.tilesize), 1)
                self.pathfinder.clear_nodes(self.map.get_map())
                result = self.pathfinder.astar(((tile_from_xcoords(self.starts[0].rect.x, self.map.tilesize),
                                                 tile_from_xcoords(self.starts[0].rect.y, self.map.tilesize)), 0),
                                               self.goals)
                self.map.change_node(tile_from_xcoords(towerxy[0], self.map.tilesize),
                                     tile_from_xcoords(towerxy[1], self.map.tilesize), 0)
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
            self.blit(tower_img, self.camera.apply_rect(tower_pos))

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
                    for i, tower_rect in enumerate(self.ui.tower_rects):
                        if (self.protein < TOWER_DATA[self.available_towers[i]][0]["upgrade_cost"]):
                            continue
                        temp_rect = tower_rect.copy()
                        temp_rect.x += self.get_size()[0] - self.ui.width
                        if temp_rect.collidepoint(event.pos):
                            self.current_tower = self.available_towers[i]
                            return -1

                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                if self.map.get_node(x_coord, y_coord) == 1:
                    self.map.upgrade_tower(x_coord, y_coord)  # don't need to upgrade tower if clicking on empty space
                    return -1

                if self.map.is_valid_tower_tile(x_coord, y_coord) == 0:
                    return -1

                if self.current_tower == None:
                    return -1

                if self.map.change_node(x_coord, y_coord, 1) == False:
                    return -1

                self.pathfinder.clear_nodes(self.map.get_map())

                for start in self.starts:
                    path = self.pathfinder.astar(((tile_from_xcoords(start.rect.x, self.map.tilesize),
                                                   tile_from_xcoords(start.rect.y, self.map.tilesize)), 0),
                                                 self.goals)
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
                self.protein -= TOWER_DATA[self.current_tower][0]["upgrade_cost"]
                self.current_tower = None

                self.buy_sound.play()
                self.make_stripped_path(self)
                self.draw_tower_bases(self)
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 3:
                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                self.map.remove_tower(x_coord, y_coord)
                self.pathfinder.clear_nodes(self.map.get_map())
                self.make_stripped_path(self)
                self.draw_tower_bases(self)
                for enemy in self.enemies:
                    enemy.recreate_path()

            elif event.button == 4:
                self.camera.zoom(0.05)

            elif event.button == 5:
                self.camera.zoom(-0.05)

        elif (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return "pause"
        
        elif event == self.game_done_event:
            return "game_over"
        
        return -1
    
class Start():
    def __init__(self, clock, game, start, enemy_type, enemy_count, spawn_delay, spawn_rate):
        self.clock = clock
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

    def update(self):
        self.time_passed += self.clock.get_time()
        if (self.time_passed >= self.next_spawn and (self.infinity or self.enemy_count > 0)):
            self.game.enemies.add(Enemy(
                clock = self.clock,
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
    
    def get_rect(self):
        return self.rect

class Goal(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.game = game
        self.groups = game.goals
        super().__init__(self.groups)
        self.rect = pg.Rect(x, y, w, h)

    def get_node(self):
        return ((round(self.rect.x / self.game.map.tilesize), round(self.rect.y / self.game.map.tilesize)), 0)
