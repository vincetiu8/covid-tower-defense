import sys

from sprites import *
from tilemap import *
from towers import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        self.map = TiledMap(path.join(MAP_FOLDER, 'test.tmx'))
        self.map_img = self.map.make_map()
        self.map_objects = self.map.make_objects()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        
        self.protein = PROTEIN
        self.lives = LIVES
        
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "start":
                self.start = Start(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, 1)
            if tile_object.name == "goal":
                self.goal = Goal(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                
        self.camera = Camera(self.map.width, self.map.height)
        self.path = astar(self.map.get_map(), (int(self.start.x / TILESIZE), int(self.start.y / TILESIZE)),
                          (int(self.goal.x / TILESIZE), int(self.goal.y / TILESIZE)))
    
    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
        
        # game over screen, loops until the user quits
        # setting self.game_over = False restarts the game
        self.game_over = True
        while self.game_over:
            self.draw_game_over()
            self.events()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        if (self.lives <= 0):
            self.playing = False

        self.all_sprites.update()
        self.start.update()
        self.enemies.update()
        self.towers.update()
        self.projectiles.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("FPS: {:.2f}  Protein: {}".format(self.clock.get_fps(), self.protein))
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        
        applied_goal_rect = self.camera.apply_rect(self.goal.rect)

        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.start.rect))
        pg.draw.rect(self.screen, GREEN, applied_goal_rect)
        
        # draws # of lives left on goal
        lives_font = pg.font.Font(None, TILESIZE)
        lives_text = lives_font.render(str(self.lives), 1, BLACK)
        self.screen.blit(lives_text, (applied_goal_rect.left + TILESIZE // 4,
                                      applied_goal_rect.top + TILESIZE // 4))

        for i, node in enumerate(self.path):
            if (i > 0 and i < len(self.path) - 1):
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(
                    pg.Rect(node[0] * TILESIZE, node[1] * TILESIZE, TILESIZE, TILESIZE)))

        for enemy in self.enemies:
            self.screen.blit(enemy.image, self.camera.apply_rect(enemy.rect))
            pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for tower in self.towers:
            pg.draw.rect(self.screen, RED, self.camera.apply_rect(tower.rect))
            if (tower.current_enemy != None):
                pg.draw.line(self.screen, WHITE, (round_to_mtilesize(tower.x), round_to_mtilesize(tower.y)), (round_to_mtilesize(tower.current_enemy.x), round_to_mtilesize(tower.current_enemy.y)))

        for projectile in self.projectiles:
            pg.draw.rect(self.screen, LIGHTGREY, self.camera.apply_rect(projectile.rect))

        # self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # for sprite in self.all_sprites:
        #     self.screen.blit(sprite.image, self.camera.apply(sprite))
        # self.screen.blit(self.map_objects, self.camera.apply_rect(self.map_rect))
        pg.display.flip()
        
    def draw_game_over(self):
        game_over_font_1 = pg.font.Font(None, 140)
        game_over_font_2 = pg.font.Font(None, 60)
            
        game_over_text_1 = game_over_font_1.render("GAME OVER", 1, WHITE)
        game_over_text_2 = game_over_font_2.render("Press R to Restart", 1, WHITE)
           
        self.screen.blit(game_over_text_1, (40, 40)) # hardcoding coords lol
        self.screen.blit(game_over_text_2, (40, 140))
            
        pg.display.flip()
        
    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                    
            if self.playing:
                if event.type == pg.MOUSEBUTTONUP:
                    pos = pg.mouse.get_pos()
                    tile_map = self.map.get_map()
                    
                    if tile_map[tile_from_coords(pos[0])][tile_from_coords(pos[1])] == 0:
                        tile_map[tile_from_coords(pos[0])][tile_from_coords(pos[1])] = 1
                        path = astar(tile_map, (tile_from_xcoords(self.start.x), tile_from_xcoords(self.start.y)),
                                        (tile_from_xcoords(self.goal.x), tile_from_xcoords(self.goal.y)))
                        
                        if (path != False and self.protein >= BUY_COST):
                            self.path = path
                            Tower(
                                game = self, 
                                x = round_to_tilesize(pos[0]),
                                y = round_to_tilesize(pos[1]),
                                bullet_spawn_speed = 0.2, 
                                bullet_speed = 25, 
                                bullet_size = 8, 
                                damage = [1, 2, 3],
                                range = 200,
                                upgrade_cost = 5)
                            self.protein -= BUY_COST
                            
                            for enemy in self.enemies:
                                enemy.recreate_path()
                        else: # reverts tile map to previous state if no enemy path could be found
                            tile_map[tile_from_coords(pos[0])][tile_from_coords(pos[1])] = 0
                    else:
                        for tower in self.towers: # Checks each tower if the mouse is hovering over it
                            if tower.rect.collidepoint(pos):
                                tower.upgrade()
                        
            else:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.game_over = False


# create the game object
g = Game()
while True:
    g.new()
    g.run()
