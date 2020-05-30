from data.settings import *
import textwrap

class UI:
    def __init__(self, game, width, offset):
        self.game = game
        self.width = width
        self.offset = offset
        self.wave = 1
        self.dialogues = []
        for i, wave in enumerate(self.game.level_data["waves"]):
            if isinstance(wave[0], str):
                self.dialogues.append(i)
        self.max_wave = game.max_wave - len(self.dialogues)
        self.lives = game.lives
        self.protein = game.protein
        
        self.next_wave_btn_enabled = True
        self.next_wave_btn_changed = False
        self.active = True
        
        self.tower_size = round((width - 2 * offset) / 2)
        self.tower_rects = [pg.Rect(self.offset, self.offset * 6 + HEART_IMG.get_size()[0] * 3 + i * (self.offset + self.tower_size), self.tower_size, self.tower_size) for i, tower in enumerate(self.game.available_towers)]
        
        self.next_wave_rect = None
        self.tower = None
        
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
            i = 0
            while i < len(self.dialogues) and self.dialogues[i] < self.wave:
                i += 1
            self.wave = self.game.wave - len(self.dialogues[:i + 1]) + 1
            self.lives = self.game.lives
            self.protein = self.game.protein
            self.ui = self.get_ui()
            
        if not self.game.in_a_wave and self.wave > 0:
            self.update_timer()

    def select_tower(self, x, y):
        try:
            self.tower = self.game.map.get_tower_map()[x][y]
            self.ui = self.get_ui()
        except:
            pass

    def deselect_tower(self):
        self.tower = None
        self.ui = self.get_ui()

    def get_ui(self):
        size = HEART_IMG.get_size()[0]
        font = pg.font.Font(FONT, size * 2)
        
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

        if self.tower == None:
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

        else:
            tower_dat = TOWER_DATA[self.tower.name]
            tower_img = pg.transform.scale(tower_dat["stages"][self.tower.stage]["image"], (self.width - MENU_OFFSET * 2, self.width - MENU_OFFSET * 2))
            ui.blit(tower_img, self.tower_rects[0])

            font = pg.font.Font(FONT, int(HEART_IMG.get_size()[0] * 1.3))
            text = font.render("Damage: " + str(tower_dat["stages"][self.tower.stage]["damage"]), 1, WHITE)
            ui.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height()))

            text = font.render("Speed: " + str(tower_dat["stages"][self.tower.stage]["attack_speed"]) + "s", 1, WHITE)
            ui.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + MENU_OFFSET + text.get_height()))

            text = font.render("Hits: " + str(self.tower.hits), 1, WHITE)
            ui.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + MENU_OFFSET * 2 + text.get_height() * 2))

            text = font.render("Kills: " + str(self.tower.kills), 1, WHITE)
            ui.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + MENU_OFFSET * 3 + text.get_height() * 3))

            refund = 0
            for stage in range(self.tower.stage + 1):
                refund += round(tower_dat["stages"][stage]["upgrade_cost"] / 2)
            sell_button, self.sell_rect = self.make_button("Sell: " + str(refund), True)
            self.sell_rect.bottom = SCREEN_HEIGHT - MENU_OFFSET * 4 - self.sell_rect.height
            ui.blit(sell_button, self.sell_rect)

            if self.tower.stage < 2:
                upgrade_cost = tower_dat["stages"][self.tower.stage + 1]["upgrade_cost"]
                upgrade_button, self.upgrade_rect = self.make_button("Upgrade: " + str(upgrade_cost), self.game.protein >= upgrade_cost)
                self.upgrade_rect.bottom = SCREEN_HEIGHT - MENU_OFFSET * 5 - self.sell_rect.height * 2
                ui.blit(upgrade_button, self.upgrade_rect)
        
        text = "Next Wave"
        if self.wave == 0:
            text = "Start Wave"

        next_wave_button, self.next_wave_rect = self.make_button(text, self.next_wave_btn_enabled)
        self.next_wave_rect.bottom = SCREEN_HEIGHT - MENU_OFFSET * 3
        ui.blit(next_wave_button, self.next_wave_rect)

        return ui

    def make_button(self, string, enabled):
        font = pg.font.Font(FONT, int(HEART_IMG.get_size()[0] * 1.3))
        text = font.render(string, 1, WHITE)
        btn = pg.transform.scale(LEVEL_BUTTON_IMG, (self.width - MENU_OFFSET * 2,
                                                              text.get_height())).copy().convert_alpha()
        btn.blit(text, text.get_rect(center=btn.get_rect().center))

        if not enabled:
            btn.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)

        rect = btn.get_rect()
        rect.left = MENU_OFFSET

        return btn, rect

    def update_timer(self):
        timer_width = (self.width - 10) * (WAVE_DELAY * 1000 - self.game.time_passed) // (WAVE_DELAY * 1000)
        timer_height = 8
        pg.draw.rect(self.ui, DARK_GREY,
                     pg.Rect(10, self.next_wave_rect.y - timer_height, self.width - 10, timer_height))
        pg.draw.rect(self.ui, GREEN,
                    pg.Rect(10, self.next_wave_rect.y - timer_height, timer_width, timer_height))

    def event(self, pos):
        if pos[0] < 0 or pos[0] > self.width or pos[1] < 0 or pos[1] > SCREEN_HEIGHT - MENU_OFFSET * 2:
            return -2

        if self.tower == None:
            for i, tower_rect in enumerate(self.tower_rects):
                if tower_rect.collidepoint(pos):
                    return i

        else:
            if self.sell_rect.collidepoint(pos):
                return "sell"

            elif self.tower.stage < 2 and self.upgrade_rect.collidepoint(pos):
                return "upgrade"

        if self.next_wave_btn_enabled and self.next_wave_rect.collidepoint(pos):
            return "start_wave"

        return -1

class Textbox(pg.Surface):
    def __init__(self, game):
        self.game = game
        self.enabled = False
        self.writing = False
        self.width = SCREEN_WIDTH - MENU_OFFSET * 2
        self.height = GRID_MARGIN_Y # Should probably change this later.
        super().__init__((self.width, self.height))
        self.set_text("")
        self.yoffset = 0
        self.draw()

    def update(self):
        if self.enabled and self.yoffset < self.height + MENU_OFFSET:
            self.yoffset += 10
            return

        elif not self.enabled and self.yoffset > 0:
            self.yoffset -= 10
            return

        elif self.position < len(self.text):
            self.position += 1
            self.current_text = self.text[:self.position]
            self.draw()

    def toggle(self, state):
        if state:
            self.enabled = True
        else:
            self.enabled = False

    def draw(self):
        temp_img = pg.transform.scale(LEVEL_BUTTON_IMG, (self.width, self.height))
        self.blit(temp_img, (0, 0))

        height = MENU_OFFSET
        self.font = pg.font.Font(FONT, MENU_TEXT_SIZE * 2)
        text = textwrap.fill(self.current_text, 30 - round(MENU_TEXT_SIZE / 30))  # No idea how to really calculate this.
        text = text.split("\n")
        for i, part in enumerate(text):
            rendered_text = self.font.render(part, 1, WHITE)
            self.blit(rendered_text, (MENU_TEXT_SIZE, height))
            height += MENU_TEXT_SIZE * 2

    def set_text(self, text):
        self.text = text
        self.current_text = ""
        self.position = 1
        self.writing = True


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
