from data.settings import *
from data.display import *

class Options(Display):
    def __init__(self):
        super().__init__()
        self.fullscreen = TickBoxOption("Fullscreen")
        self.music_vol = SliderOption("Music Vol", min_val = 0, max_val = 1, slider_pos = SLIDER_BAR_WIDTH - SLIDER_WIDTH)
        self.sfx_vol = SliderOption("SFX Vol", min_val = 0, max_val = 1, slider_pos = SLIDER_BAR_WIDTH - SLIDER_WIDTH)
        
        self.back_rect = pg.Rect((20, 20), OPTIONS_BACK_IMGS[0].get_size())
        
        self.brain_img = BRAIN_IMG
        self.brain_img.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)
        
        self.fullscreen_surf = self.fullscreen.draw()
        self.music_vol_surf = self.music_vol.draw()
        self.sfx_vol_surf = self.sfx_vol.draw()
        self.surfs = [self.fullscreen_surf, self.music_vol_surf, self.sfx_vol_surf]
        
        self.prev_display = None
        
    def new(self, args):
        self.prev_display = args[0]
        
    def draw(self):
        self.fill(BLACK)
        
        title_font = pg.font.Font(FONT, 160)
        title_text = title_font.render("OPTIONS", 1, WHITE)
        
        self.blit(self.brain_img, ((SCREEN_WIDTH - self.brain_img.get_width()) / 2, (SCREEN_HEIGHT - self.brain_img.get_height()) / 2))
        self.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) / 2, 0))
        
        back_hover = self.back_rect.collidepoint(pg.mouse.get_pos())
        self.blit(OPTIONS_BACK_IMGS[back_hover], self.back_rect)
        
        x = 100
        y = 150
        
        for surf in self.surfs:
            if surf.are_coords_unset():
                surf.set_coords(x, y)
                
            self.blit(surf, (x, y))
            y += surf.get_height() + OPTIONS_SEPARATION
        
        return self
    
    def event(self, event):
        if self.music_vol.event(event) != -1:
            self.music_vol_surf = self.music_vol_surf.draw()
            
        if self.sfx_vol.event(event) != -1:
            self.sfx_vol_surf = self.sfx_vol_surf.draw()
            update_sfx_vol(self.sfx_vol.get_val()) # settings.py function
                    
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.back_rect.collidepoint(event.pos):
                    return self.prev_display
                if self.fullscreen.event(event) != -1:
                    self.fullscreen_surf = self.fullscreen.draw()
                    toggle_fullscreen()
        return -1
    
class Option(pg.Surface):
    def __init__(self, label):
        self.x = 0
        self.y = 0
        
        label_font = pg.font.Font(FONT, 80)
        self.label_text = label_font.render(label, 1, WHITE)
        
    def init_surf(self, width, height):
        super().__init__((width, height), pg.SRCALPHA)
        self.convert_alpha()
        
    def are_coords_unset(self):
        return (self.x == 0 and self.y == 0)
    
    def set_coords(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self): # to be overrided
        pass
    
    def event(self, event): # to be overrided
        return -1
    
class SliderOption(Option):
    def __init__(self, label, min_val, max_val, slider_pos):
        super().__init__(label)
        
        self.min_val = min_val
        self.max_val = max_val
        self.slider_pos = slider_pos # Slider's x pos ranges from 0 to (SLIDER_BAR_WIDTH - SLIDER_WIDTH)
        self.held_down = False

        self.slider_bar_rect = pg.Rect(self.label_text.get_width() + 20, 15, SLIDER_BAR_WIDTH, SLIDER_BAR_HEIGHT)
        
        self.slider_rect = None
        self.slider_true_rect = None
        self.update_slider_rect()
        
        super().init_surf(self.slider_bar_rect.x + SLIDER_BAR_WIDTH + 5, SLIDER_HEIGHT + 5)
        
    def get_val(self): 
        return (self.min_val + (self.max_val - self.min_val) * self.slider_pos / (SLIDER_BAR_WIDTH - SLIDER_WIDTH))
    
    def set_coords(self, x, y):
        super().set_coords(x, y)
        self.slider_true_rect = pg.Rect(self.slider_rect.x + self.x, self.y, SLIDER_WIDTH, SLIDER_HEIGHT)
        
    def update_slider_rect(self): # Has to be updated every time the slider is moved
        self.slider_rect = pg.Rect(self.label_text.get_width() + 20 + self.slider_pos, 0, SLIDER_WIDTH, SLIDER_HEIGHT)
        self.slider_true_rect = pg.Rect(self.slider_rect.x + self.x, self.y, SLIDER_WIDTH, SLIDER_HEIGHT)
        
    def draw(self):
        self.fill((0, 0, 0, 0))
        
        self.blit(self.label_text, (0, -15))
        pg.draw.rect(self, WHITE, self.slider_bar_rect, 5)
        pg.draw.rect(self, WHITE, self.slider_rect, 0)
        
        return self
    
    # Events should always be passed to SliderOption regardless of type
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.slider_true_rect.collidepoint(event.pos):
                    self.held_down = True
                    
        elif event.type == pg.MOUSEBUTTONUP:
            self.held_down = False
            
        elif event.type == pg.MOUSEMOTION:
            if self.held_down:
                mouse_pos_x = event.pos[0] - self.x - self.slider_bar_rect.x # Corrects mouse_pos_x to the same reference as the slider_bar
                self.slider_pos = min(SLIDER_BAR_WIDTH - SLIDER_WIDTH, max(0, mouse_pos_x))
                self.update_slider_rect()
                return True
        
        return -1
        
class TickBoxOption(Option):
    def __init__(self, label):
        super().__init__(label)
        self.ticked = False
        
        self.tick_box_rect = pg.Rect(self.label_text.get_width() + 20, 5, TICK_BOX_SIZE, TICK_BOX_SIZE) # Needs some buffer on the top
        self.tick_box_true_rect = None
        
        super().init_surf(self.tick_box_rect.x + TICK_BOX_SIZE + 5, TICK_BOX_SIZE + 10) # Needs some buffer on the right and bottom
        
    def is_ticked(self):
        return self.ticked
    
    def set_coords(self, x, y):
        super().set_coords(x, y)
        self.tick_box_true_rect = pg.Rect(self.tick_box_rect.x + self.x, self.tick_box_rect.y + self.y, TICK_BOX_SIZE, TICK_BOX_SIZE)
        
    def draw(self):
        self.fill((0, 0, 0, 0))
        small_font = pg.font.Font(FONT, 70)
        
        self.blit(self.label_text, (0, -10))
        pg.draw.rect(self, WHITE, self.tick_box_rect, 8)
        
        if self.ticked:
            self.blit(small_font.render("X", 1, WHITE), (self.tick_box_rect.x + 15, self.tick_box_rect.y - 10))
            
        return self
    
    # Events should only be passed to TickBoxOptions if there are MOUSEBUTTONDOWN 1 events
    def event(self, event):
        if self.tick_box_true_rect.collidepoint(event.pos):
            self.ticked = not self.ticked
            return True
        
        return -1
