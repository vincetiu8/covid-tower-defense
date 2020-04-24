from data.settings import *

class GameStop(pg.Surface):
    def __init__(self):
        super().__init__((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.restart_rect = pg.Rect(200, 400, RESTART_BTN_IMGS[0][0].get_width(), RESTART_BTN_IMGS[0][0].get_height())
        self.back_rect = pg.Rect(750, 400, BACK_BTN_IMGS[0][0].get_width(), BACK_BTN_IMGS[0][0].get_height())
        
        self.circle_cache = {}
        
        self.text_1 = None
        self.text_2 = None
        self.restart_text = None
        self.back_text_1 = None
        self.back_text_2 = None
        
        self.font_1 = pg.font.Font(FONT, 200)
        self.font_2 = pg.font.Font(FONT, 60)
        
        self.alpha = 0
        self.alpha_speed = 0
    
    def draw(self):
        self.alpha = min(255, self.alpha + self.alpha_speed)
        self.draw_grid()
        
        self.draw_btns()
        self.draw_text()
        
        self.set_alpha(self.alpha)
        
        #self.main_screen.blit(self, (0, 0))
        
    def draw_grid(self):
        color = DARK_GREEN
        if self.lost:
            color = DARK_RED
            
        for x in range(0, SCREEN_WIDTH, 60):
            pg.draw.line(self, color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pg.draw.line(self, color, (0, y), (SCREEN_WIDTH, y))
        
    def init_text(self, str_1, str_2):
        color = WHITE
        if self.lost:
            color = RED
            
        self.text_1 = self.render_text(str_1, self.font_1, color, BLACK)
        self.text_2 = self.render_text(str_2, self.font_2, color, BLACK)
        
        self.restart_text = self.render_text("Restart", self.font_2, color, BLACK)
        self.back_text_1 = self.render_text("Back to", self.font_2, color, BLACK)
        self.back_text_2 = self.render_text("Level Select", self.font_2, color, BLACK)
        
    def draw_text(self):
        self.blit(self.text_1, (self.center_text_x(0, SCREEN_WIDTH, self.text_1), 70))
        self.blit(self.text_2, (self.center_text_x(0, SCREEN_WIDTH, self.text_2), 260))
        
        self.blit(self.restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, self.restart_text),
                                    self.center_text_y(self.restart_rect.y, self.restart_rect.h, self.restart_text)))
        
        self.blit(self.back_text_1, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_1),
                                    self.center_text_y(self.back_rect.y - self.back_text_2.get_rect().h / 3, self.back_rect.h, self.back_text_1)))
        self.blit(self.back_text_2, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_2),
                                    self.center_text_y(self.back_rect.y + self.back_text_1.get_rect().h / 3, self.back_rect.h, self.back_text_2)))
        
    def draw_btns(self):
        hover_restart = self.restart_rect.collidepoint(pg.mouse.get_pos())
        hover_back = self.back_rect.collidepoint(pg.mouse.get_pos())
        
        restart_btn_img = RESTART_BTN_IMGS[self.lost][hover_restart]
        back_btn_img = BACK_BTN_IMGS[self.lost][hover_back]
        
        self.blit(restart_btn_img, (self.restart_rect[0], self.restart_rect[1]))
        self.blit(back_btn_img, (self.back_rect[0], self.back_rect[1]))
        
    def is_done_fading(self):
        return self.alpha == 255
    
    def can_register_clicks(self):
        return self.alpha >= 80
    
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
                    return "restart"
                elif self.back_rect.collidepoint(event.pos):
                    return "back to level select"
                
        return False

class Pause(GameStop):
    def __init__(self):
        super().__init__()
        
        self.resume_rect = pg.Rect(500, 300, RESUME_BTN_IMGS[0].get_width(), RESUME_BTN_IMGS[0].get_height())
        self.resume_text = None
        
        self.lost = False
        
        self.alpha_speed = 12
        
        self.init_text("GAME PAUSED", "")
        
    def draw(self):
        self.fill(BLACK)
        super().draw()
        
    def draw_text(self):
        super().draw_text()
        self.blit(self.resume_text, (self.center_text_x(self.resume_rect.x, self.resume_rect.w, self.resume_text),
                                    self.center_text_y(self.resume_rect.y, self.resume_rect.h, self.resume_text)))
        
    def init_text(self, str_1, str_2):
        super().init_text(str_1, str_2)
        self.resume_text = self.render_text("Resume", self.font_2, WHITE, BLACK)
        
    def draw_btns(self):
        super().draw_btns()
        
        hover_resume = self.resume_rect.collidepoint(pg.mouse.get_pos())
        resume_btn_img = RESUME_BTN_IMGS[hover_resume]
        self.blit(resume_btn_img, (self.resume_rect[0], self.resume_rect[1]))
        
    def event(self, event):
        result = super().event(event)
        
        if result == False:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.resume_rect.collidepoint(event.pos):
                        return "resume"
        
        return result
        
class GameOver(GameStop):
    def __init__(self, lost, cause_of_death):
        super().__init__()
        
        self.lost = lost
        self.cause_of_death = cause_of_death
        
        self.heartbeat_x = 0
        
        self.heart_beep_sfx = pg.mixer.Sound(AUDIO_HEART_BEEP_PATH)
        self.flatline_sfx = pg.mixer.Sound(AUDIO_FLATLINE_PATH)
        self.heart_beep_sfx.set_volume(0.6)
        self.flatline_sfx.set_volume(0.6)
        
        self.alpha_speed = 3
        
        if self.lost:
            self.init_text("YOU DIED", "Cause of death: " + self.cause_of_death)
        else:
            self.init_text("YOU SURVIVED", "But the infection still continues...")
        
    def play_sfx(self):
        play_beep_x = [20, 332, 724, 1160]
        play_flatline_x = -1
        
        if self.lost:
            play_flatline_x = play_beep_x[2]
            play_beep_x = play_beep_x[:2]
        
        if self.heartbeat_x in play_beep_x:
            self.heart_beep_sfx.play()
        elif self.heartbeat_x == play_flatline_x:
            self.flatline_sfx.play()
            
    def stop_sfx(self):
        self.heart_beep_sfx.stop()
        self.flatline_sfx.stop()
        
    def draw(self):
        self.fill(BLACK)
        self.heartbeat_x = min(1280, self.heartbeat_x + 4)
        self.draw_heartbeat()
        
        super().draw()
        
        self.play_sfx()
        
    def draw_heartbeat(self):
        image = HEART_MONITOR_NORMAL_IMG
        if self.lost:
            image = HEART_MONITOR_FLATLINE_IMG
        
        self.blit(image, (0, 0))
        pg.draw.rect(self, BLACK, (int(self.heartbeat_x), 0, SCREEN_WIDTH - int(self.heartbeat_x), SCREEN_HEIGHT))
        
    def event(self, event):
        result = super().event(event)
        
        if result != False:
            self.stop_sfx()
        
        return result
