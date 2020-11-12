import sys

from data.pathfinding import *
from data.game_misc import *
from data.game import Game
from data.tilemap import *
from data.towers import *
from data.game_stop import Pause, GameOver
from data.menus import *
from data.dev_tools import TowerPreviewMenu, EnemyPreviewMenu
from data.options import Options
from data.settings import SAVE_DATA

class Main:
    def __init__(self):
        pg.key.set_repeat(500, 100)
        self.main_clock = pg.time.Clock()
        self.clock = pg.time.Clock()
        self.playing = False
        self.started_game = False
        self.game_surf = None # only used to draw static game screen when fading into game_stop screens
        self.black_alpha_surf = pg.Surface((SAVE_DATA["width"], SAVE_DATA["height"]))

        self.display = MainDisplay()

        self.start_menu = StartMenu(self.clock)
        self.menu = Menu()
        self.game = Game(self.clock)
        self.game_over = GameOver()
        self.pause = Pause()
        self.tower_preview = TowerPreviewMenu(self.clock)
        self.enemy_preview = EnemyPreviewMenu(self.clock)
        self.upgrades_menu = UpgradesMenu()
        self.purchase_menu = PurchaseMenu()
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
            "upgrades_menu":    self.upgrades_menu,
            "purchase_menu":    self.purchase_menu,
            "tower_select":     self.tower_select,
            "options":          self.options
        }
        
        self.display_keys_reverse = {
            self.menu:      "menu",
            self.pause:     "pause",
            self.game_over: "game_over",
            self.start_menu:"start_menu"
        }

        self.set_display(self.start_menu, [self.menu, False])

        self.result = None
        
        self.fading_out = False
        self.fading_in = False
        self.black_alpha = 0
        self.fade_out_speed = [10, 40]
        self.fade_in_speed = [30, 50]
        self.fade_ind = 0

        self.game_surf = None

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
        
        self.display.display.fill((0, 0, 0))
        if self.current_display is self.game_over or self.current_display is self.pause:
            self.display.display.blit(self.game_surf, (0, 0))

        if self.current_display is self.game or self.current_display is self.menu:
            surf = self.current_display.draw()
        else:
            surf = pg.transform.scale(self.current_display.draw(), (SAVE_DATA["width"], SAVE_DATA["height"]))
        self.display.display.blit(surf, (0, 0))
        
        if self.fading_out:
            if self.black_alpha == 255:
                self.fading_out = False
                self.fading_in = True
                self.set_display(self.display_keys[self.result], self.args)
            else:
                self.black_alpha = min(255, self.black_alpha + self.fade_out_speed[self.fade_ind])
                
            self.black_alpha_surf.fill((0, 0, 0))
            self.black_alpha_surf.set_alpha(self.black_alpha)
            self.display.display.blit(self.black_alpha_surf, (0, 0))
            
        elif self.fading_in:
            if self.black_alpha == 0:
                self.fading_in = False
            else:
                self.black_alpha = max(0, self.black_alpha - self.fade_in_speed[self.fade_ind])
                
            self.black_alpha_surf.fill((0, 0, 0))
            self.black_alpha_surf.set_alpha(self.black_alpha)
            self.display.display.blit(self.black_alpha_surf, (0, 0))
            
        pg.display.flip()

    def events(self):
        if self.fading_in or self.fading_out:
            return
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                break

            elif event.type == pg.USEREVENT + 4: # Detects if graphics option changed
                self.black_alpha_surf = pg.Surface((SAVE_DATA["width"], SAVE_DATA["height"]))
                self.game.event(event)
                self.menu.event(event)

            else:
                if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP or event.type == pg.MOUSEMOTION:
                    event.pos = (round(event.pos[0] / self.display.screen_ratio), round(event.pos[1] / self.display.screen_ratio))
                temp_result = self.current_display.event(event)

                if temp_result != -1:
                    self.result = temp_result
                    self.args = []

                    if self.result == "game" or self.result == "resume":
                        self.args.extend([(self.menu.get_over_level(), self.tower_select.get_difficulty()), self.result == "resume", self.tower_select.get_selected_towers()])
                    elif self.result == "tower_select":
                        self.args.extend([self.menu.get_over_level(), self.menu.get_difficulty()])
                    elif self.result == "options":
                        self.args.extend([self.display_keys_reverse[self.current_display]])
                    elif self.result == "game_over":
                        self.game_surf = self.game.draw()
                        self.args.extend([self.game.draw(), self.current_display == self.options,
                                     self.game.get_lives() == 0, self.game.get_cause_of_death(), (self.game.level, self.game.difficulty, self.game.protein)])
                    elif self.result == "pause":
                        self.game_surf = self.game.draw()
                        self.args.extend([self.game.draw(), self.current_display == self.options])
                    elif self.result == "menu":
                        self.args.append(self.current_display in self.display_keys_reverse)
                    
                    # don't do fade out for the following transitions:
                    # transitioning from game --> pause/game_over
                    # transitioning from pause --> game (resuming, not restarting)
                    if (self.current_display == self.game and (self.result == "pause" or self.result == "game_over")) or (self.current_display == self.pause and self.result == "resume"):
                        self.set_display(self.display_keys[self.result], self.args)
                    else:
                        self.fade_ind = 1
                        if self.current_display == self.game_over: # transitioning from game_over has a slower fade speed
                            self.fade_ind = 0
                            
                        self.fading_out = True
                    
    def set_display(self, display, args):
        display.new(args)
        self.current_display = display

    def quit(self):
        with open(SAVE_FILEPATH, 'w') as out_file:
            json.dump(SAVE_DATA, out_file, indent=4)
        pg.quit()
        sys.exit()
