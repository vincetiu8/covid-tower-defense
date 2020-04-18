from settings import *

class GameOver(pg.Surface):
    def __init__(self, cause_of_death, main_screen):
        super().__init__((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.cause_of_death = cause_of_death
        self.main_screen = main_screen
        
        self.restart_rect = pg.Rect(300, 400, RESTART_BTN_IMG.get_width(), RESTART_BTN_IMG.get_height())
        self.back_rect = pg.Rect(700, 400, BACK_BTN_IMG.get_width(), BACK_BTN_IMG.get_height())
        self.alpha = 0
    
    def draw(self):
        self.fill(BLACK)
        self.alpha = min(255, self.alpha + 3)
        
        font_1 = pg.font.Font(GAME_OVER_FONT, 200)
        font_2 = pg.font.Font(GAME_OVER_FONT, 60)
            
        text_1 = font_1.render("YOU DIED", 1, RED)
        text_2 = font_2.render("Cause of death: " + self.cause_of_death.title(), 1, RED)
        
        restart_text = font_2.render("Restart", 1, RED)
        back_text_1 = font_2.render("Back to", 1, RED)
        back_text_2 = font_2.render("Level Select", 1, RED)
        
        restart_btn_img = RESTART_BTN_IMG
        back_btn_img = BACK_BTN_IMG
        
        if self.restart_rect.collidepoint(pg.mouse.get_pos()):
            restart_btn_img = RESTART_BTN_HOVER_IMG
        if self.back_rect.collidepoint(pg.mouse.get_pos()):
            back_btn_img = BACK_BTN_HOVER_IMG
        
        self.blit(text_1, (self.center_text_x(0, SCREEN_WIDTH, text_1), 70))
        self.blit(text_2, (self.center_text_x(0, SCREEN_WIDTH, text_2), 260))
        
        self.blit(restart_btn_img, (self.restart_rect[0], self.restart_rect[1]))
        self.blit(back_btn_img, (self.back_rect[0], self.back_rect[1]))
        self.blit(restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, restart_text),
                                 self.center_text_y(self.restart_rect.y, self.restart_rect.h, restart_text)))
        self.blit(back_text_1, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, back_text_1),
                                self.center_text_y(self.back_rect.y - back_text_2.get_rect().h / 3, self.back_rect.h, back_text_1)))
        self.blit(back_text_2, (self.center_text_x(self.back_rect.x + 10, self.back_rect.w, back_text_2),
                                self.center_text_y(self.back_rect.y + back_text_1.get_rect().h / 3, self.back_rect.h, back_text_2)))
            
        self.set_alpha(self.alpha)
        
        self.main_screen.blit(self, (0, 0))
        
    def is_done_fading(self):
        return self.alpha == 255
    
    def center_text_x(self, offset, width, text):
        return offset + (width - text.get_rect().w) / 2
    
    def center_text_y(self, offset, height, text):
        return offset + (height - text.get_rect().h) / 2
    
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.restart_rect.collidepoint(event.pos):
                    return "restart"
                elif self.back_rect.collidepoint(event.pos):
                    return "back to level select"
                
        return False
