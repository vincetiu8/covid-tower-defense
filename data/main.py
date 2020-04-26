import sys
import textwrap

from data.pathfinding import *
from data.ui import *
from data.game import *
from data.tilemap import *
from data.towers import *
from data.game_stop import *
from data.dev_tools import Tower_Preview

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
        self.tower_preview_button = pg.Rect((600, 100), self.level_button_rect.size)
        self.level_descs = [None for i in range(len(LEVEL_DATA))]
        self.over_level = -1
        self.tower_preview = None

    def update(self):
        self.update_level()
        if self.tower_preview != None:
            self.tower_preview.update()

    def draw(self):
        self.screen.fill((0, 0, 0))

        if not self.started:
            self.screen.blit(self.camera.apply_image(START_SCREEN_IMG), self.camera.apply_rect(pg.Rect(0, 0, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)))
            return

        lives_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w)
        level_text = lives_font.render("Levels", 1, WHITE)
        self.screen.blit(self.camera.apply_image(level_text), self.camera.apply_tuple((START_SCREEN_IMG.get_rect().w / 2 - level_text.get_rect().center[0], 75 - level_text.get_rect().center[1])))

        for i, button in enumerate(self.level_buttons):
            self.screen.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(button))
            lives_text = lives_font.render(str(i + 1), 1, WHITE)
            self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple((button.center[0] - lives_text.get_rect().center[0], button.center[1] - lives_text.get_rect().center[1])))

        self.screen.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.tower_preview_button))
        lives_text = lives_font.render("Tower", 1, WHITE)
        self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0], self.tower_preview_button.center[1] - lives_text.get_rect().center[1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Preview", 1, WHITE)
        self.screen.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0], self.tower_preview_button.center[1] - lives_text.get_rect().center[1] + lives_text.get_rect().height - MENU_OFFSET)))

        if self.tower_preview != None:
            temp_surf = self.tower_preview.draw()
            self.screen.blit(temp_surf, (MENU_OFFSET, MENU_OFFSET))
            return

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
        title_font = pg.font.Font(FONT, MENU_TEXT_SIZE * 2)
        texts = []
        title_text = title_font.render(level_data["title"], 1, WHITE)
        texts.append(title_text)
        height += title_text.get_height() + MENU_OFFSET

        description_font = pg.font.Font(FONT, MENU_TEXT_SIZE)
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
        if self.tower_preview != None:
            self.tower_preview.event(event)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and not self.started:
                self.started = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
                if self.tower_preview_button.collidepoint(mouse_pos):
                    if self.tower_preview == None:
                        self.tower_preview = Tower_Preview()
                    else:
                        self.tower_preview = None

                elif self.tower_preview != None:
                    return -1

                return self.over_level

            elif event.button == 4:
                self.camera.zoom(0.05, event.pos)

            elif event.button == 5:
                self.camera.zoom(-0.05, event.pos)

        return -1