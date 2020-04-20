from settings import *

class GameOver(pg.Surface):
    def __init__(self, lost, main_screen, cause_of_death):
        super().__init__((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.clock = pg.time.Clock()
        self.lost = lost
        self.cause_of_death = cause_of_death
        self.main_screen = main_screen
        
        self.restart_rect = pg.Rect(250, 400, RESTART_BTN_IMGS[0][0].get_width(), RESTART_BTN_IMGS[0][0].get_height())
        self.back_rect = pg.Rect(700, 400, BACK_BTN_IMGS[0][0].get_width(), BACK_BTN_IMGS[0][0].get_height())
        
        self.heart_beep_sfx = pg.mixer.Sound(path.join(AUDIO_FOLDER, "heart_beep.wav"))
        self.flatline_sfx = pg.mixer.Sound(path.join(AUDIO_FOLDER, "flatline.wav"))
        self.heart_beep_sfx.set_volume(0.6)
        self.flatline_sfx.set_volume(0.6)
        
        self.circle_cache = {}
        
        self.text_1 = None
        self.text_2 = None
        self.restart_text = None
        self.back_text_1 = None
        self.back_text_2 = None
        self.init_text() # init text only once so no need to rerender every time
        
        self.alpha = 0
        self.heartbeat_x = 0
        
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
        self.clock.tick(80)
        self.fill(BLACK)
        
        self.alpha = min(255, self.alpha + 3)
        self.heartbeat_x = min(1280, self.heartbeat_x + 4)
        
        self.draw_heartbeat()
        self.draw_grid()
        
        self.draw_btns()
        self.draw_text()
        
        self.set_alpha(self.alpha)
        
        self.main_screen.blit(self, (0, 0))
        self.play_sfx()
        
    def draw_grid(self):
        color = DARK_GREEN
        if self.lost:
            color = DARK_RED
            
        for x in range(0, SCREEN_WIDTH, 60):
            pg.draw.line(self, color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pg.draw.line(self, color, (0, y), (SCREEN_WIDTH, y))
            
    def draw_heartbeat(self):
        image = HEART_MONITOR_NORMAL_IMG
        if self.lost:
            image = HEART_MONITOR_FLATLINE_IMG
        
        self.blit(image, (0, 0))
        pg.draw.rect(self, BLACK, (int(self.heartbeat_x), 0, SCREEN_WIDTH - int(self.heartbeat_x), SCREEN_HEIGHT))
    
    def draw_text(self):
        self.blit(self.text_1, (self.center_text_x(0, SCREEN_WIDTH, self.text_1), 70))
        self.blit(self.text_2, (self.center_text_x(0, SCREEN_WIDTH, self.text_2), 260))
        
        self.blit(self.restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, self.restart_text),
                                    self.center_text_y(self.restart_rect.y, self.restart_rect.h, self.restart_text)))
        
        self.blit(self.back_text_1, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_1),
                                    self.center_text_y(self.back_rect.y - self.back_text_2.get_rect().h / 3, self.back_rect.h, self.back_text_1)))
        self.blit(self.back_text_2, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, self.back_text_2),
                                    self.center_text_y(self.back_rect.y + self.back_text_1.get_rect().h / 3, self.back_rect.h, self.back_text_2)))
        
    def init_text(self):
        color = WHITE
        str_1 = "YOU SURVIVED"
        str_2 = "But the infection still continues..."
        
        if self.lost:
            color = RED
            str_1 = "YOU DIED"
            str_2 = "Cause of death: " + self.cause_of_death.title()
            
        font_1 = pg.font.Font(GAME_OVER_FONT, 200)
        font_2 = pg.font.Font(GAME_OVER_FONT, 60)
        
        self.text_1 = self.render_text(str_1, font_1, color, BLACK)
        self.text_2 = self.render_text(str_2, font_2, color, BLACK)
        
        self.restart_text = self.render_text("Restart", font_2, color, BLACK)
        self.back_text_1 = self.render_text("Back to", font_2, color, BLACK)
        self.back_text_2 = self.render_text("Level Select", font_2, color, BLACK)
        
    def draw_btns(self):
        hover_restart = self.restart_rect.collidepoint(pg.mouse.get_pos())
        hover_back = self.back_rect.collidepoint(pg.mouse.get_pos())
        
        restart_btn_img = RESTART_BTN_IMGS[self.lost][hover_restart]
        back_btn_img = BACK_BTN_IMGS[self.lost][hover_back]
        
        self.blit(restart_btn_img, (self.restart_rect[0], self.restart_rect[1]))
        self.blit(back_btn_img, (self.back_rect[0], self.back_rect[1]))
        
    def is_done_fading(self):
        return self.alpha == 255
    
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
                    self.stop_sfx()
                    return "restart"
                elif self.back_rect.collidepoint(event.pos):
                    self.stop_sfx()
                    return "back to level select"
                
        return False
