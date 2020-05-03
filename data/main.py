import sys

from data.pathfinding import *
from data.ui import *
from data.game import Game
from data.tilemap import *
from data.towers import *
from data.game_stop import *
from data.menus import *
from data.dev_tools import TowerPreview, EnemyPreview, LevelPreview

class Main:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.key.set_repeat(500, 100)
        self.clock = pg.time.Clock()
        self.game_clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.playing = False
        self.started_game = False
        self.game_surf = None # only used to draw static game screen when fading into game_stop screens
        
        self.start_menu = StartMenu()
        self.menu = Menu()
        self.game = Game(self.game_clock)
        self.game_over = GameOver()
        self.pause = Pause()
        self.tower_preview = TowerPreview(self.game_clock)
        self.enemy_preview = EnemyPreview(self.game_clock)
        self.level_preview = LevelPreview(self.game_clock)
        self.tower_select = TowerSelectMenu()
        
        self.display_keys = {
            "menu":             self.menu,
            "resume":           self.game,
            "game":             self.game,
            "game_over":        self.game_over,
            "pause":            self.pause,
            "tower_preview":    self.tower_preview,
            "enemy_preview":    self.enemy_preview,
            "level_preview":    self.level_preview,
            "tower_select":     self.tower_select
        }
        
        self.current_display = self.start_menu
        
    def run(self):
        self.clock.tick(FPS)
        self.game_clock.tick()
        self.events()
        self.update()
        self.game_clock.tick()
        self.draw()

    def update(self):
        self.current_display.update()
        
    def draw(self):
        pg.display.set_caption("FPS: {:.2f}".format(self.clock.get_fps()))
        
        self.screen.fill((0, 0, 0))
        surf = self.current_display.draw()
        self.screen.blit(surf, (0, 0))
            
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                break

            else:
                result = self.current_display.event(event)
                
                if result != -1:
                    args = []
                    if result == "game" or result == "resume":
                        args.extend([self.menu.get_over_level(), result == "resume", self.tower_select.get_selected_towers()])
                    elif result == "game_over":
                        args.extend([self.game.draw(), self.game.get_lives() == 0, self.game.get_cause_of_death()])
                    elif result == "pause":
                        args.append(self.game.draw())
                        
                    self.set_display(self.display_keys[result], args)
                    
    def set_display(self, display, args):
        display.new(args)
        self.current_display = display

    def quit(self):
        pg.quit()
        sys.exit()
