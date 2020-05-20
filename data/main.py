import sys

from data.pathfinding import *
from data.game_misc import *
from data.game import Game
from data.tilemap import *
from data.towers import *
from data.game_stop import Pause, GameOver
from data.menus import *
from data.dev_tools import TowerEditMenu, EnemyEditMenu, LevelEditMenu, TowerPreviewMenu, EnemyPreviewMenu
from data.options import Options
from data.settings import SAVE_DATA

class Main:
    def __init__(self):
        pg.key.set_repeat(500, 100)
        self.main_clock = pg.time.Clock()
        self.clock = pg.time.Clock()
        #self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.playing = False
        self.started_game = False
        self.game_surf = None # only used to draw static game screen when fading into game_stop screens
        
        self.start_menu = StartMenu()
        self.menu = Menu()
        self.game = Game(self.clock)
        self.game_over = GameOver()
        self.pause = Pause()
        self.tower_preview = TowerPreviewMenu(self.clock)
        self.enemy_preview = EnemyPreviewMenu(self.clock)
        self.tower_edit = TowerEditMenu(self.clock)
        self.enemy_edit = EnemyEditMenu(self.clock)
        self.level_edit = LevelEditMenu(self.clock)
        self.tower_select = TowerSelectMenu()
        self.options = Options()
        
        self.display_keys = {
            "menu":             self.menu,
            "resume":           self.game,
            "game":             self.game,
            "game_over":        self.game_over,
            "pause":            self.pause,
            "tower_preview":    self.tower_preview,
            "enemy_preview":    self.enemy_preview,
            "tower_edit":       self.tower_edit,
            "enemy_edit":       self.enemy_edit,
            "level_edit":       self.level_edit,
            "tower_select":     self.tower_select,
            "options":          self.options
        }
        
        self.display_keys_reverse = {
            self.menu:          "menu",
            self.pause:         "pause"
        }
        
        self.current_display = self.start_menu
        
    def run(self):
        self.main_clock.tick(FPS)
        self.clock.tick()
        self.events()
        self.update()
        self.clock.tick()
        self.draw()

    def update(self):
        self.current_display.update()
        
    def draw(self):
        pg.display.set_caption("FPS: {:.2f}".format(self.main_clock.get_fps()))
        
        SCREEN.fill((0, 0, 0))
        surf = self.current_display.draw()
        SCREEN.blit(surf, (0, 0))
            
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
                    elif result == "tower_select":
                        args.append(self.menu.get_over_level())
                    elif result == "options":
                        args.append(self.display_keys_reverse[self.current_display])
                    elif result == "game_over":
                        args.extend([self.game.draw(), self.current_display == self.options,
                                     self.game.get_lives() == 0, self.game.get_cause_of_death(), self.game.level])
                    elif result == "pause":
                        args.extend([self.game.draw(), self.current_display == self.options])
                        
                    self.set_display(self.display_keys[result], args)
                    
    def set_display(self, display, args):
        display.new(args)
        self.current_display = display

    def quit(self):
        with open(path.join(GAME_FOLDER, "save.json"), 'w') as out_file:
            json.dump(SAVE_DATA, out_file, indent=4)
        pg.quit()
        sys.exit()
