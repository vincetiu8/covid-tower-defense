from settings import *

class GameOver(pg.Surface):
    def __init__(self, cause_of_death, main_screen):
        super().__init__((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cause_of_death = cause_of_death
        self.restart_rect = pg.Rect(300, 400, RESTART_IMG.get_width(), RESTART_IMG.get_rect().h)
        print(self.restart_rect)
        self.main_screen = main_screen
        self.alpha = 0
    
    def draw(self):
        self.fill(BLACK)
        self.alpha = min(255, self.alpha + 3)
        
        font_1 = pg.font.Font(GAME_OVER_FONT, 200)
        font_2 = pg.font.Font(GAME_OVER_FONT, 60)
            
        text_1 = font_1.render("YOU DIED", 1, RED)
        text_2 = font_2.render("Cause of death: " + self.cause_of_death.title(), 1, RED)
        
        restart_text = font_2.render("Restart", 1, RED)
        
        self.blit(text_1, (self.center_text_x(0, SCREEN_WIDTH, text_1), 70))
        self.blit(text_2, (self.center_text_x(0, SCREEN_WIDTH, text_2), 260))
        
        self.blit(RESTART_IMG, (self.restart_rect[0], self.restart_rect[1]))
        self.blit(restart_text, (self.center_text_x(self.restart_rect.x, self.restart_rect.w, restart_text),
                                 self.center_text_y(self.restart_rect.y, self.restart_rect.h, restart_text)))
            
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
                
        return False
