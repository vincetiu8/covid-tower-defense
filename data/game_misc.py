from data.settings import *

class UI:
    def __init__(self, game, width, offset):
        self.game = game
        self.width = width
        self.offset = offset
        self.wave = game.wave
        self.max_wave = game.max_wave
        self.lives = game.lives
        self.protein = game.protein
        
        self.next_wave_btn_enabled = True
        self.next_wave_btn_changed = False
        self.active = True
        
        self.tower_size = round((width - 2 * offset) / 2)
        self.tower_rects = [pg.Rect(self.offset, self.offset * 6 + HEART_IMG.get_size()[0] * 3 + i * (self.offset + self.tower_size), self.tower_size, self.tower_size) for i, tower in enumerate(self.game.available_towers)]
        
        self.next_wave_rect = None
        
        self.ui = self.get_ui()
        self.set_active(self.active)

    def set_active(self, bool):
        self.active = bool
        if bool:
            self.rect = RIGHT_ARROW_IMG.get_rect(
                topright=(self.game.get_size()[0] - self.width - self.offset, self.offset))

        else:
            self.rect = LEFT_ARROW_IMG.get_rect(topright=(self.game.get_size()[0] - self.offset, self.offset))
            
    def set_next_wave_btn(self, state):
        self.next_wave_btn_enabled = state
        self.next_wave_btn_changed = True

    def update(self):
        if (self.lives != self.game.lives or self.protein != self.game.protein or self.next_wave_btn_changed):
            self.next_wave_btn_changed = False
            self.wave = self.game.wave
            self.lives = self.game.lives
            self.protein = self.game.protein
            self.ui = self.get_ui()
            
        if not self.game.in_a_wave and self.wave > 0:
            self.update_timer()

    def get_ui(self):
        size = HEART_IMG.get_size()[0]
        font = pg.font.Font(FONT, size * 2)
        next_wave_font = pg.font.Font(FONT, int(size * 1.3))
        
        ui = pg.Surface((self.width, self.game.get_size()[1] - 2 * self.offset))
        ui.fill(DARK_GREY)
        
        # Draws waves, lives, protein text
        waves_text = font.render("Wave {}/{}".format(self.wave + 1, self.max_wave), 1, WHITE)

        ui.blit(waves_text, (self.offset, self.offset))
        ui.blit(HEART_IMG, (self.offset, self.offset * 4 + size))
        ui.blit(PROTEIN_IMG, (self.offset, self.offset * 5 + size * 2))

        lives_text = font.render(str(self.game.lives), 1, WHITE)
        lives_text = pg.transform.scale(lives_text,
                                        (round(lives_text.get_size()[0] * size / lives_text.get_size()[1]), size))
        ui.blit(lives_text, (self.offset * 2 + size, self.offset * 4 + size))

        protein_text = font.render(str(self.game.protein), 1, WHITE)
        protein_text = pg.transform.scale(protein_text,
                                          (round(protein_text.get_size()[0] * size / protein_text.get_size()[1]), size))
        ui.blit(protein_text, (self.offset * 2 + size, self.offset * 5 + size * 2))
        
        # Draws towers
        for i, tower in enumerate(self.game.available_towers):
            tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"], self.tower_rects[i].size)
            if (self.game.protein < TOWER_DATA[tower]["stages"][0]["upgrade_cost"]):
                tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
            ui.blit(tower_img, self.tower_rects[i])
            temp_rect = self.tower_rects[i].copy()
            temp_rect.x += self.tower_size + self.offset
            ui.blit(PROTEIN_IMG, temp_rect)
            cost_text = font.render(str(TOWER_DATA[tower]["stages"][0]["upgrade_cost"]), 1, WHITE)
            temp_rect.y += size + self.offset
            ui.blit(cost_text, temp_rect)
        
        # Draws "Next Wave" btn
        text = "Next Wave"
        if self.wave == 0:
            text = "Start Wave"
            
        next_wave_text = next_wave_font.render(text, 1, WHITE)
        next_wave_btn = pg.transform.scale(LEVEL_BUTTON_IMG, (next_wave_text.get_width() + BTN_PADDING * 2,             
                                                              next_wave_text.get_height())).copy().convert_alpha()
        next_wave_btn.blit(next_wave_text, next_wave_text.get_rect(center = next_wave_btn.get_rect().center))
        
        if not self.next_wave_btn_enabled:
            next_wave_btn.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)
            
        next_wave_btn_x = (self.width - next_wave_btn.get_width()) / 2
        next_wave_btn_y = ui.get_height() - self.offset - next_wave_btn.get_height()
        ui.blit(next_wave_btn, (next_wave_btn_x, next_wave_btn_y))
        
        self.next_wave_rect = pg.Rect(next_wave_btn_x, next_wave_btn_y, next_wave_btn.get_width(), next_wave_btn.get_height())

        return ui
    
    def update_timer(self):
        timer_width = (self.width - 10) * (WAVE_DELAY * 1000 - self.game.time_passed) // (WAVE_DELAY * 1000)
        timer_height = 8
        pg.draw.rect(self.ui, DARK_GREY,
                     pg.Rect(10, self.next_wave_rect.y - self.offset - timer_height, self.width - 10, timer_height))
        pg.draw.rect(self.ui, GREEN,
                    pg.Rect(10, self.next_wave_rect.y - self.offset - timer_height, timer_width, timer_height))

class Explosion(pg.sprite.Sprite):
    def __init__(self, game, x, y, rad):
        super().__init__(game.explosions)
        self.clock = game.clock
        self.x = x - rad / 2
        self.y = y - rad / 2
        self.rad = rad
        self.state = 0
        self.surf = pg.Surface((rad, rad)).convert_alpha()

    def update(self):
        passed_time = self.clock.get_time() / 1000
        self.state += passed_time / EXPLOSION_TIME
        if self.state >= 1:
            self.kill()
        else:
            self.surf.fill((255, 0, 0, 127 * self.state))

    def get_surf(self):
        return self.surf