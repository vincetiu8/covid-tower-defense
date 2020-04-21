from settings import *

class UI:
    def __init__(self, game, width, offset):
        self.game = game
        self.width = width
        self.offset = offset
        self.wave = game.wave
        self.max_wave = game.max_wave
        self.lives = game.lives
        self.protein = game.protein
        self.active = True
        self.tower_size = round((width - 2 * offset) / 2)
        self.tower_rects = [pg.Rect(self.offset, self.offset * 5 + HEART_IMG.get_size()[0] * 3 + i * (self.offset + self.tower_size), self.tower_size, self.tower_size) for i, tower in enumerate(self.game.available_towers)]
        self.ui = self.get_ui()
        self.set_active(self.active)

    def set_active(self, bool):
        self.active = bool
        if bool:
            self.rect = RIGHT_ARROW_IMG.get_rect(
                topright=(self.game.screen.get_size()[0] - self.width - self.offset, self.offset))

        else:
            self.rect = LEFT_ARROW_IMG.get_rect(topright=(self.game.screen.get_size()[0] - self.offset, self.offset))

    def update(self):
        if (self.lives != self.game.lives or self.protein != self.game.protein):
            self.wave = self.game.wave
            self.lives = self.game.lives
            self.protein = self.game.protein
            self.ui = self.get_ui()

    def get_ui(self):
        size = HEART_IMG.get_size()[0]
        font = pg.font.Font(None, size * 2)
        
        ui = pg.Surface((self.width, self.game.screen.get_size()[1] - 2 * self.offset))
        ui.fill(DARKGREY)
        
        waves_text = font.render("Wave {}/{}".format(self.wave, self.max_wave), 1, WHITE)

        ui.blit(waves_text, (self.offset, self.offset))
        ui.blit(HEART_IMG, (self.offset, self.offset * 3 + size))
        ui.blit(PROTEIN_IMG, (self.offset, self.offset * 4 + size * 2))

        lives_text = font.render(str(self.game.lives), 1, WHITE)
        lives_text = pg.transform.scale(lives_text,
                                        (round(lives_text.get_size()[0] * size / lives_text.get_size()[1]), size))
        ui.blit(lives_text, (self.offset * 2 + size, self.offset * 3 + size))

        protein_text = font.render(str(self.game.protein), 1, WHITE)
        protein_text = pg.transform.scale(protein_text,
                                          (round(protein_text.get_size()[0] * size / protein_text.get_size()[1]), size))
        ui.blit(protein_text, (self.offset * 2 + size, self.offset * 4 + size * 2))

        for i, tower in enumerate(self.game.available_towers):
            tower_img = pg.transform.scale(TOWER_DATA[tower][0]["base_image"], self.tower_rects[i].size)
            tower_img.blit(pg.transform.scale(TOWER_DATA[tower][0]["gun_image"], self.tower_rects[i].size), (0, 0))
            if (self.game.protein < TOWER_DATA[tower][0]["upgrade_cost"]):
                tower_img.fill(DARKGREY, None, pg.BLEND_RGB_MULT)
            ui.blit(tower_img, self.tower_rects[i])
            temp_rect = self.tower_rects[i].copy()
            temp_rect.x += self.tower_size + self.offset
            ui.blit(PROTEIN_IMG, temp_rect)
            cost_text = font.render(str(TOWER_DATA[tower][0]["upgrade_cost"]), 1, WHITE)
            temp_rect.y += size + self.offset
            ui.blit(cost_text, temp_rect)

        return ui
