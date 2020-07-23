from data.settings import *
from data.display import *

class GridDisplay(Display):
    def __init__(self):
        super().__init__()
        self.circle_cache = {}
        self.lost = False

    def new(self, args):
        self.no_fade_in = args[1]

        if self.no_fade_in:
            self.alpha = 255
        else:
            self.alpha = 0

    def draw(self):
        self.set_alpha(self.alpha)

    def draw_grid(self):
        color = DARK_GREEN
        if self.lost:
            color = DARK_RED

        for x in range(0, SCREEN_WIDTH, 60):
            pg.draw.line(self, color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pg.draw.line(self, color, (0, y), (SCREEN_WIDTH, y))

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

    def is_done_fading(self):
        return self.alpha == 255

    def can_click(self):
        return self.alpha > 125 or self.alpha == 0

class GameStop(GridDisplay):
    def __init__(self):
        super().__init__()
        
        self.restart_rect = pg.Rect(200, 400, RESTART_BTN_IMGS[0][0].get_width(), RESTART_BTN_IMGS[0][0].get_height())
        self.back_rect = pg.Rect(750, 400, BACK_BTN_IMGS[0][0].get_width(), BACK_BTN_IMGS[0][0].get_height())
        
        self.text_1 = None
        self.text_2 = None
        self.restart_text = None
        self.back_text_1 = None
        self.back_text_2 = None
        
        self.font_1 = pg.font.Font(FONT, 200)
        self.font_2 = pg.font.Font(FONT, 60)
        
    def new(self, args):
        super().new(args)
        self.hover_back = False
        self.hover_restart = False
    
    def draw(self):
        self.draw_grid()
        self.draw_btns()
        self.draw_text()
        super().draw()

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
        self.blit(self.texts[0], (self.center_text_x(0, SCREEN_WIDTH, self.texts[0]), 50))
        for i, text in enumerate(self.texts[1:]):
            self.blit(text, (self.center_text_x(0, SCREEN_WIDTH, text), 230 + i * 50))
        
        self.blit(self.restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, self.restart_text),
                                    self.center_text_y(self.restart_rect.y, self.restart_rect.h, self.restart_text)))
        
        self.blit(self.back_text_1, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_1),
                                    self.center_text_y(self.back_rect.y - self.back_text_2.get_rect().h / 3, self.back_rect.h, self.back_text_1)))
        self.blit(self.back_text_2, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_2),
                                    self.center_text_y(self.back_rect.y + self.back_text_1.get_rect().h / 3, self.back_rect.h, self.back_text_2)))
        
    def draw_btns(self):
        self.blit(RESTART_BTN_IMGS[self.lost][self.hover_restart], self.restart_rect)
        self.blit(BACK_BTN_IMGS[self.lost][self.hover_back], self.back_rect)
    
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
        self.fill(BLACK)
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
        self.blit(self.resume_text, (self.center_text_x(self.resume_rect.x, self.resume_rect.w, self.resume_text),
                                    self.center_text_y(self.resume_rect.y, self.resume_rect.h, self.resume_text)))
        
    def init_text(self, str_1, str_2):
        super().init_text(str_1, str_2)
        self.resume_text = self.render_text("Resume", self.font_2, WHITE, BLACK)
        
    def draw_btns(self):
        super().draw_btns()
        self.blit(RESUME_BTN_IMGS[self.hover_resume], self.resume_rect)
        self.blit(OPTIONS_IMGS[self.hover_options], self.options_rect)
        
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
        self.fading_out = None #indicates if game over surface is fading out
        
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
        LEVEL_CLEAR_SFX.stop()
        
    def new(self, args):
        super().new(args)
        
        self.fading_out = False
        self.heartbeat_x = 0
        self.lost, self.cause_of_death = args[2], args[3]

        highscore_beaten = False
        level, difficulty, protein = args[4]
        
        if not self.lost:
            LEVEL_CLEAR_SFX.play()
            completed = False
            protein_goal = False
            
            if difficulty < 2 and level == 10:
                SAVE_DATA["latest_level_unlocked"][difficulty + 1] = 0
                
            if level > SAVE_DATA["latest_level_completed"][difficulty]:
                SAVE_DATA["latest_level_completed"][difficulty] = level
                SAVE_DATA["latest_level_unlocked"][difficulty] = level + 1
                SAVE_DATA["max_dna"] += DNA_ON_COMPLETION[difficulty]
                completed = True
                
            if (SAVE_DATA["highscores"][level][difficulty] < LEVEL_DATA[level]["protein_goal"][difficulty]
                and protein >= LEVEL_DATA[level]["protein_goal"][difficulty]):
                SAVE_DATA["max_dna"] += DNA_ON_PROTEIN_GOAL[difficulty]
                protein_goal = True
                
            self.init_dna_text(difficulty, completed, protein_goal)

            if SAVE_DATA["highscores"][level][difficulty] <= protein:
                SAVE_DATA["highscores"][level][difficulty] = protein
                highscore_beaten = True

        if self.lost:
            self.init_text("YOU DIED", "Cause of death: " + self.cause_of_death, "Highest Protein Count: " + str(SAVE_DATA["highscores"][level][difficulty]))
        elif highscore_beaten:
            self.init_text("YOU SURVIVED", "But the infection still continues...", "New Highest Protein Count: " + str(SAVE_DATA["highscores"][level][difficulty]))
        else:
            self.init_text("YOU SURVIVED", "But the infection still continues...", "Protein Count: " + str(protein), "Highest Protein Count: " + str(SAVE_DATA["highscores"][level][difficulty]))
        
    def draw(self):
        self.fill(BLACK)
        self.alpha = min(255, self.alpha + self.alpha_speed)
        self.heartbeat_x = min(1280, self.heartbeat_x + 4)
        self.draw_heartbeat()
        
        super().draw()
        
        if not self.fading_out:
            self.play_sfx()
        
        return self
    
    def init_dna_text(self, difficulty, completed, protein_goal):
        font_3 = pg.font.Font(FONT, 30)
        self.dna_texts = [None, None, None]
        if completed or protein_goal:
            self.dna_texts[0] = self.render_text("DNA Bonuses:", font_3, WHITE, BLACK)
        
        if completed:
            self.dna_texts[1] = self.render_text("+{} - Body Part Cleared".format(DNA_ON_COMPLETION[difficulty]), font_3, WHITE, BLACK)
            
        if protein_goal:
            self.dna_texts[2] = self.render_text("+{} - Protein Count Goal Reached".format(DNA_ON_PROTEIN_GOAL[difficulty]), font_3, WHITE, BLACK)
    
    def draw_text(self):
        if not self.lost:
            y = 5
            
            for dna_text in self.dna_texts:
                if dna_text != None:
                    self.blit(dna_text, (SCREEN_WIDTH - dna_text.get_width() - 10, y))
                    y += dna_text.get_height() - 10
                
        super().draw_text()
        
    def draw_heartbeat(self):
        image = HEART_MONITOR_NORMAL_IMG
        if self.lost:
            image = HEART_MONITOR_FLATLINE_IMG
        
        self.blit(image, (0, 0))
        pg.draw.rect(self, BLACK, (int(self.heartbeat_x), 0, SCREEN_WIDTH - int(self.heartbeat_x), SCREEN_HEIGHT))
        
    def event(self, event):
        if not self.can_click():
            return -1
        
        result = super().event(event)
        
        if result != -1:
            self.fading_out = True
            self.stop_sfx()
        
        return result
