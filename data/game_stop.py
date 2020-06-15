from data.settings import *
from data.display import *

class GameStop(Display):
    def __init__(self):
        super().__init__()
        
        self.restart_rect = pg.Rect(200, 400, RESTART_BTN_IMGS[0][0].get_width(), RESTART_BTN_IMGS[0][0].get_height())
        self.back_rect = pg.Rect(750, 400, BACK_BTN_IMGS[0][0].get_width(), BACK_BTN_IMGS[0][0].get_height())
        self.game_stop_surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.circle_cache = {}
        
        self.text_1 = None
        self.text_2 = None
        self.restart_text = None
        self.back_text_1 = None
        self.back_text_2 = None
        
        self.font_1 = pg.font.Font(FONT, 200)
        self.font_2 = pg.font.Font(FONT, 60)
        
    def new(self, args):
        self.game_surf = args[0]
        self.no_fade_in = args[1]
        
        self.hover_back = False
        self.hover_restart = False
        
        self.alpha = 0
        if self.no_fade_in:
            self.alpha = 255
    
    def draw(self):
        self.draw_grid()
        self.draw_btns()
        self.draw_text()
        
        self.game_stop_surf.set_alpha(self.alpha)
        
        self.blit(self.game_surf, (0, 0))
        self.blit(self.game_stop_surf, (0, 0))
        
    def draw_grid(self):
        color = DARK_GREEN
        if self.lost:
            color = DARK_RED
            
        for x in range(0, SCREEN_WIDTH, 60):
            pg.draw.line(self.game_stop_surf, color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pg.draw.line(self.game_stop_surf, color, (0, y), (SCREEN_WIDTH, y))
        
    def init_text(self, *args):
        color = WHITE
        if self.lost:
            color = RED

        self.texts = []
        self.texts.append(self.render_text(args[0], self.font_1, color, BLACK))

        for arg in args[1:]:
            self.texts.append(self.render_text(arg, self.font_2, color, BLACK))
        
        self.restart_text = self.render_text("Restart", self.font_2, color, BLACK)
        self.back_text_1 = self.render_text("Back to", self.font_2, color, BLACK)
        self.back_text_2 = self.render_text("Level Select", self.font_2, color, BLACK)
        
    def draw_text(self):
        self.game_stop_surf.blit(self.texts[0], (self.center_text_x(0, SCREEN_WIDTH, self.texts[0]), 70))
        for i, text in enumerate(self.texts[1:]):
            self.game_stop_surf.blit(text, (self.center_text_x(0, SCREEN_WIDTH, text), 260 + i * 50))
        
        self.game_stop_surf.blit(self.restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, self.restart_text),
                                    self.center_text_y(self.restart_rect.y, self.restart_rect.h, self.restart_text)))
        
        self.game_stop_surf.blit(self.back_text_1, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_1),
                                    self.center_text_y(self.back_rect.y - self.back_text_2.get_rect().h / 3, self.back_rect.h, self.back_text_1)))
        self.game_stop_surf.blit(self.back_text_2, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_2),
                                    self.center_text_y(self.back_rect.y + self.back_text_1.get_rect().h / 3, self.back_rect.h, self.back_text_2)))
        
    def draw_btns(self):
        self.game_stop_surf.blit(RESTART_BTN_IMGS[self.lost][self.hover_restart], self.restart_rect)
        self.game_stop_surf.blit(BACK_BTN_IMGS[self.lost][self.hover_back], self.back_rect)
        
    def is_done_fading(self):
        return self.alpha == 255
    
    def can_click(self):
        return self.alpha > 125 or self.alpha == 0
    
    def center_text_x(self, offset, width, text):
        return offset + (width - text.get_rect().w) / 2
    
    def center_text_y(self, offset, height, text):
        return offset + (height - text.get_rect().h) / 2
    
    # these next two functions are for drawing a border around the text
    # idk how it works, i got it off stackoverflow
    def circlepoints(self, r):
        r = int(round(r))
        if r in self.circle_cache:
            return self.circle_cache[r]
        
        x, y, e = r, 0, 1 - r
        self.circle_cache[r] = points = []
        
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
                
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        
        return points

    def render_text(self, text, font, color, border_color, opx = 2):
        text_surf = font.render(text, True, color).convert_alpha()
        w = text_surf.get_width() + 2 * opx
        h = font.get_height()

        border_surf = pg.Surface((w, h + 2 * opx)).convert_alpha()
        border_surf.fill((0, 0, 0, 0))

        surf = border_surf.copy()

        border_surf.blit(font.render(text, True, border_color).convert_alpha(), (0, 0))

        for dx, dy in self.circlepoints(opx):
            surf.blit(border_surf, (dx + opx, dy + opx))

        surf.blit(text_surf, (opx, opx))
        return surf
    
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.restart_rect.collidepoint(event.pos):
                    BTN_SFX.play()
                    return "game"
                elif self.back_rect.collidepoint(event.pos):
                    BTN_SFX.play()
                    return "menu"
        elif event.type == pg.MOUSEMOTION:
            self.hover_restart = self.restart_rect.collidepoint(event.pos)
            self.hover_back = self.back_rect.collidepoint(event.pos)
                
        return -1

class Pause(GameStop):
    def __init__(self):
        super().__init__()
        self.fade_out_done_event = pg.event.Event(pg.USEREVENT + 2)
        
        self.resume_rect = pg.Rect((500, 300), RESUME_BTN_IMGS[0].get_size())
        self.options_rect = pg.Rect((1100, 20), OPTIONS_IMGS[0].get_size())
        self.resume_text = None
        
        self.lost = False
        self.fading_out = False
        
        self.alpha_speed = 20
        
        self.init_text("GAME PAUSED", "")
        
    def new(self, args):
        super().new(args)
        self.hover_options = False
        self.hover_resume = False
        
    def draw(self):
        self.game_stop_surf.fill(BLACK)
        if self.fading_out:
            self.alpha = max(0, self.alpha - self.alpha_speed)
            if self.alpha == 0:
                pg.event.post(self.fade_out_done_event)
                self.fading_out = False
        else:
            self.alpha = min(255, self.alpha + self.alpha_speed)
        
        super().draw()
        return self
        
    def draw_text(self):
        super().draw_text()
        self.game_stop_surf.blit(self.resume_text, (self.center_text_x(self.resume_rect.x, self.resume_rect.w, self.resume_text),
                                    self.center_text_y(self.resume_rect.y, self.resume_rect.h, self.resume_text)))
        
    def init_text(self, str_1, str_2):
        super().init_text(str_1, str_2)
        self.resume_text = self.render_text("Resume", self.font_2, WHITE, BLACK)
        
    def draw_btns(self):
        super().draw_btns()
        self.game_stop_surf.blit(RESUME_BTN_IMGS[self.hover_resume], self.resume_rect)
        self.game_stop_surf.blit(OPTIONS_IMGS[self.hover_options], self.options_rect)
        
    def event(self, event):
        if not self.can_click():
            return -1
        
        result = super().event(event)
        
        if result == -1:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.resume_rect.collidepoint(event.pos):
                        BTN_SFX.play()
                        self.fading_out = True
                    elif self.options_rect.collidepoint(event.pos):
                        BTN_SFX.play()
                        return "options"
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.fading_out = True
            elif event.type == pg.USEREVENT + 2:
                return "resume"
            elif event.type == pg.MOUSEMOTION:
                self.hover_resume = self.resume_rect.collidepoint(event.pos)
                self.hover_options = self.options_rect.collidepoint(event.pos)
        
        return result
        
class GameOver(GameStop):
    def __init__(self):
        super().__init__()
        
        self.alpha_speed = 3
        
    def play_sfx(self):
        play_beep_x = [20, 332, 724, 1160]
        play_flatline_x = -1
        
        if self.lost:
            play_flatline_x = play_beep_x[2]
            play_beep_x = play_beep_x[:2]
        
        if self.heartbeat_x in play_beep_x:
            HEART_BEEP_SFX.play()
        elif self.heartbeat_x == play_flatline_x:
            FLATLINE_SFX.play()
            
    def stop_sfx(self):
        HEART_BEEP_SFX.stop()
        FLATLINE_SFX.stop()
        
    def new(self, args):
        super().new(args)
        
        self.heartbeat_x = 0
        self.lost, self.cause_of_death = args[2], args[3]

        highscore_beaten = False
        level, difficulty, protein = args[4]
        
        if difficulty == 0:
            multiplier = 0.5
        elif difficulty == 1:
            multiplier = 1
        else:
            multiplier = 1.5
        
        adj_protein = round(protein * multiplier)
        
        if not self.lost:
            if level == len(SAVE_DATA["levels"]) - 1:
                SAVE_DATA["levels"].append([True, False, False])
                SAVE_DATA["highscores"].append(0)

            if difficulty < 2 and not SAVE_DATA["levels"][level][difficulty + 1]:
                SAVE_DATA["levels"][level][difficulty + 1] = True

            if SAVE_DATA["highscores"][level] <= adj_protein:
                SAVE_DATA["max_dna"] += adj_protein - SAVE_DATA["highscores"][level]
                SAVE_DATA["highscores"][level] = adj_protein
                highscore_beaten = True

        if self.lost:
            self.init_text("YOU DIED", "Cause of death: " + self.cause_of_death, "High Score: " + str(SAVE_DATA["highscores"][level]))
        elif highscore_beaten:
            self.init_text("YOU SURVIVED", "But the infection still continues...", "Score: " + str(protein) + " x " + str(multiplier) + " = " + str(adj_protein), "New High Score: " + str(SAVE_DATA["highscores"][level]))
        else:
            self.init_text("YOU SURVIVED", "But the infection still continues...", "Score: " + str(protein) + " x " + str(multiplier) + " = " + str(adj_protein), "High Score: " + str(SAVE_DATA["highscores"][level]))
        
    def draw(self):
        self.game_stop_surf.fill(BLACK)
        self.alpha = min(255, self.alpha + self.alpha_speed)
        self.heartbeat_x = min(1280, self.heartbeat_x + 4)
        self.draw_heartbeat()
        
        super().draw()
        
        self.play_sfx()
        
        return self
        
    def draw_heartbeat(self):
        image = HEART_MONITOR_NORMAL_IMG
        if self.lost:
            image = HEART_MONITOR_FLATLINE_IMG
        
        self.game_stop_surf.blit(image, (0, 0))
        pg.draw.rect(self.game_stop_surf, BLACK, (int(self.heartbeat_x), 0, SCREEN_WIDTH - int(self.heartbeat_x), SCREEN_HEIGHT))
        
    def event(self, event):
        if not self.can_click():
            return -1
        
        result = super().event(event)
        
        if result != -1:
            self.stop_sfx()
        
        return result
