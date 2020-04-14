from settings import *

class UI:
    def __init__ (self, game, width, offset):
        self.game = game
        self.width = width
        self.offset = offset
        self.lives = game.lives
        self.protein = game.protein
        self.active = True
        self.ui = self.get_ui()
        self.set_active(self.active)

    def set_active(self, bool):
        self.active = bool
        if bool:
            self.rect = RIGHT_ARROW_IMG.get_rect(topright = (self.game.screen.get_size()[0] - self.width - self.offset, self.offset))

        else:
            self.rect = LEFT_ARROW_IMG.get_rect(topright = (self.game.screen.get_size()[0] - self.offset, self.offset))

    def update(self):
        if (self.lives != self.game.lives or self.protein != self.game.protein):
            self.lives = self.game.lives
            self.protein = self.game.protein
            self.ui = self.get_ui()

    def get_ui(self):
        size = HEART_IMG.get_size()[0]
        ui = pg.Surface((self.width, self.game.screen.get_size()[1] - 2 * self.offset))
        ui.fill(DARKGREY)
        ui.blit(HEART_IMG, (self.offset, self.offset))
        ui.blit(PROTEIN_IMG, (self.offset, self.offset * 2 + size))
        font = pg.font.Font(None, size * 2)
        lives_text = font.render(str(self.game.lives), 1, BLACK)
        lives_text = pg.transform.scale(lives_text, (round(lives_text.get_size()[0] * size / lives_text.get_size()[1]), size))
        ui.blit(lives_text, (self.offset * 2 + size, self.offset))

        protein_text = font.render(str(self.game.protein), 1, BLACK)
        protein_text = pg.transform.scale(protein_text, (round(protein_text.get_size()[0] * size / protein_text.get_size()[1]), size))
        ui.blit(protein_text, (self.offset * 2 + size, self.offset * 2 + size))
        return ui