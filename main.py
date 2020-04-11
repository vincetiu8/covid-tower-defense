import sys

from sprites import *
from tilemap import *
from towers import *

class Main:
    def __init__(self):
        pg.init()
        pg.key.set_repeat(500, 100)
        self.started = False
        self.playing = False
        self.start = StartScreen(pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)))
        self.draw()
        while not self.started:
            self.events()

    def run_game(self):
        self.game = Game(pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)))
        self.game.new()
        while self.playing:
            self.events()
            self.update()
            self.draw()

        while not self.playing:
            self.events()

    def update(self):
        if self.game.update() == False:
            self.game.draw_game_over()
            self.playing = False

    def draw(self):
        if not self.started:
            self.start.draw()

        if self.playing:
            self.game.draw()

        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.quit()

            elif not self.started and self.start.event(event) == False:
                self.started = True
                self.playing = True


            elif self.playing:
                self.game.event(event)

            else:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.playing = True
                        self.game.reset_map()

    def quit(self):
        pg.quit()
        sys.exit()

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)

    def draw(self):
        self.screen.blit(self.camera.apply_image(START_SCREEN_IMG), self.camera.apply_rect(pg.Rect(0, 0, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)))

    def event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                return False


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        self.map = TiledMap(path.join(MAP_FOLDER, 'test.tmx'))
        self.map_img = self.map.make_map()
        self.map_objects = self.map.make_objects()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        
        self.protein = PROTEIN
        self.lives = LIVES
        
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "start":
                self.start = Start(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, SPAWN_RATE)
            if tile_object.name == "goal":
                self.goal = Goal(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.map.width, self.map.height)
        self.path = astar(self.map.get_map(), (int(self.start.x / self.map.tilesize), int(self.start.y / self.map.tilesize)),
                          (int(self.goal.x / self.map.tilesize), int(self.goal.y / self.map.tilesize)))

    def update(self):
        # update portion of the game loop
        if (self.lives <= 0):
            return False

        self.start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()

    def draw_grid(self):
        for x in range(0, self.map.width, self.map.tilesize):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, self.map.height))
        for y in range(0, self.map.height, self.map.tilesize):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (self.map.width, y))

    def draw(self):
        pg.display.set_caption("FPS: {:.2f}  Protein: {}".format(self.clock.get_fps(), self.protein))
        self.screen.fill((0, 0, 0))
        # self.draw_grid()

        self.screen.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))
        applied_goal_rect = self.camera.apply_rect(self.goal.rect)

        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.start.rect))
        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.goal.rect))

        # draws # of lives left on goal
        lives_font = pg.font.Font(None, self.map.tilesize)
        lives_text = lives_font.render(str(self.lives), 1, BLACK)
        self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple((self.goal.rect.left + self.map.tilesize // 4,
                                      self.goal.rect.top + self.map.tilesize // 4)))

        for i, node in enumerate(self.path):
            if (i > 0 and i < len(self.path) - 1):
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(
                    pg.Rect(node[0] * self.map.tilesize, node[1] * self.map.tilesize, self.map.tilesize, self.map.tilesize)))

        for tower in self.towers:
            self.screen.blit(self.camera.apply_image(tower.base_image), self.camera.apply_rect(tower.rect))
            rotated_image = pg.transform.rotate(tower.gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            self.screen.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))
            if (tower.current_enemy != None):
                tower_pos = self.camera.apply_tuple((round_to_mtilesize(tower.x, self.map.tilesize), round_to_mtilesize(tower.y, self.map.tilesize)))
                target_pos = self.camera.apply_tuple((round_to_mtilesize(tower.current_enemy.x, self.map.tilesize), round_to_mtilesize(tower.current_enemy.y, self.map.tilesize)))
                pg.draw.line(self.screen, WHITE, tower_pos, target_pos)

        for enemy in self.enemies:
            self.screen.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for projectile in self.projectiles:
            pg.draw.rect(self.screen, LIGHTGREY, self.camera.apply_rect(projectile.rect))

        self.screen.blit(self.map_objects, self.camera.apply_rect(self.map_rect))

    def draw_game_over(self):
        game_over_font_1 = pg.font.Font(None, 140)
        game_over_font_2 = pg.font.Font(None, 60)

        game_over_text_1 = game_over_font_1.render("GAME OVER", 1, WHITE)
        game_over_text_2 = game_over_font_2.render("Press R to Restart", 1, WHITE)

        self.screen.blit(game_over_text_1, (40, 40)) # hardcoding coords lol
        self.screen.blit(game_over_text_2, (40, 140))

        pg.display.flip()

    def reset_map(self):
        self.map.clear_map()

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if (self.protein < BUY_COST):
                    return

                tile_map = self.map.get_map()
                pos = self.camera.correct_mouse(event.pos)
                x_coord = tile_from_coords(pos[0], self.map.tilesize)
                y_coord = tile_from_coords(pos[1], self.map.tilesize)

                if (tile_map[x_coord][y_coord] == 1 or self.map.change_node(x_coord, y_coord, 1) == False):
                    self.map.upgrade_tower(x_coord, y_coord) # don't need to upgrade tower if clicking on empty space
                    return

                path = astar(tile_map, (tile_from_xcoords(self.start.x, self.map.tilesize),
                                        tile_from_xcoords(self.start.y, self.map.tilesize)),
                            (tile_from_xcoords(self.goal.x, self.map.tilesize),
                              tile_from_xcoords(self.goal.y, self.map.tilesize)))

                if (path != False):
                    self.path = path

                    new_tower = Tower(
                        game = self,
                        x = round_to_tilesize(pos[0], self.map.tilesize),
                        y = round_to_tilesize(pos[1], self.map.tilesize),
                        base_image = ANITBODY_BASE_IMG,
                        gun_image = ANITBODY_GUN_IMG,
                        bullet_spawn_speed = 0.2,
                        bullet_speed = 25,
                        bullet_size = 8,
                        damage = [1, 2, 3],
                        range = 200,
                        upgrade_cost = 5)
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
                self.path = astar(tile_map, (tile_from_xcoords(self.start.x, self.map.tilesize),
                                        tile_from_xcoords(self.start.y, self.map.tilesize)),
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