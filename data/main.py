import sys

from data.pathfinding import *
from data.ui import *
from data.game import *
from data.tilemap import *
from data.towers import *
from data.game_stop import *
from data.menus import *

class Main:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.key.set_repeat(500, 100)
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.playing = False
        self.started_game = False
        self.game_surf = None # only used to draw static game screen when fading into game_stop screens
        
        self.start_menu = StartMenu()
        self.menu = Menu()
        self.game = Game()
        self.game_over = GameOver()
        self.pause = Pause()
        
        self.display_keys = {
            "menu":         self.menu,
            "resume":       self.game,
            "game":         self.game,
            "game_over":    self.game_over,
            "pause":        self.pause
        }
        
        self.current_display = self.start_menu
        
    def run(self):
        self.events()
        self.update()
        self.draw()

    def update(self):
        self.current_display.update()
        
    def draw(self):
        self.clock.tick(FPS)
        pg.display.set_caption("FPS: {:.2f}".format(self.clock.get_fps()))
        
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
                        args.extend([self.menu.get_over_level(), result == "resume"])
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
