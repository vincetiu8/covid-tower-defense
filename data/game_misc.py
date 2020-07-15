from data.settings import *
import textwrap

class UI:
    def __init__(self, game, offset):
        self.game = game
        self.offset = offset
        self.wave = 0
        self.max_wave = game.max_wave
        self.lives = game.lives
        self.protein = game.protein
        
        self.next_wave_btn_enabled = True
        self.next_wave_btn_changed = False
        self.active = True
        
        self.tower_size = round(9 * offset)
        self.tower_rects = [pg.Rect(self.offset, i * (self.offset + self.tower_size), self.tower_size, self.tower_size) for i, tower in enumerate(self.game.available_towers)]
        
        self.next_wave_rect = None
        self.tower = None

        self.size = HEART_IMG.get_size()[0]
        self.font = pg.font.Font(FONT, self.size * 2)
        self.width = 0

        self.generate_header()
        self.generate_body()
        self.generate_next_wave_wrapper()

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
        if self.wave != self.game.wave:
            self.generate_header()
            self.generate_next_wave_wrapper()

        if not self.game.in_a_wave and self.wave != 0:
            self.generate_next_wave()

    def select_tower(self, x, y):
        tower = self.game.map.get_tower(x, y)
        if tower is not self.tower:
            self.tower = tower
            self.generate_body_wrapper()

    def deselect_tower(self):
        self.tower = None
        self.generate_body_wrapper()

    def regen_surfs(self):
        self.ui = pg.Surface((self.width, SCREEN_HEIGHT - self.offset * 2))
        self.header = pg.Surface((self.width, self.offset * 7 + self.size))
        self.body = pg.Surface((self.width, self.ui.get_height() - self.offset * 13 - self.size))
        self.next_wave = pg.Surface((self.width, self.offset * 6))

    def generate_header_wrapper(self):
        self.generate_header()
        self.get_ui()

    def generate_body_wrapper(self):
        self.generate_body()
        self.get_ui()

    def generate_next_wave_wrapper(self):
        self.generate_next_wave()
        self.get_ui()

    def generate_header(self):
        # Draws waves, lives, protein text
        waves_text = self.font.render("Wave {}/{}".format(min(self.wave + 1, self.max_wave), self.max_wave), 1, WHITE)

        width = max(waves_text.get_width() + self.offset * 2, 225)
        if width != self.width:
            self.width = width
            self.regen_surfs()

        self.header.fill(DARK_GREY)
        self.header.blit(waves_text, waves_text.get_rect(midtop=(self.width / 2, 0)))
        self.header.blit(HEART_IMG, (self.offset, self.offset * 3 + self.size))
        lives_text = self.font.render(str(self.game.lives), 1, WHITE)
        lives_text = pg.transform.scale(lives_text,
                                        (round(lives_text.get_size()[0] * self.size / lives_text.get_size()[1]), self.size))
        self.header.blit(lives_text, (self.offset * 2 + self.size, self.offset * 3 + self.size))

        self.header.blit(PROTEIN_IMG, (self.offset * 3 + self.size + lives_text.get_width(), self.offset * 3 + self.size))
        protein_text = self.font.render(str(self.game.protein), 1, WHITE)
        protein_text = pg.transform.scale(protein_text,
                                          (round(protein_text.get_size()[0] * self.size / protein_text.get_size()[1]), self.size))
        self.header.blit(protein_text, (self.offset * 4 + self.size * 2 + lives_text.get_width(), self.offset * 3 + self.size))

    def generate_body(self):
        self.body.fill(DARK_GREY)
        if self.tower is None:
            # Draws towers
            for i, tower in enumerate(self.game.available_towers):
                tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"], self.tower_rects[i].size)
                if (self.game.protein < round(TOWER_DATA[tower]["stages"][0]["upgrade_cost"] * (1 + self.game.difficulty * 0.25))):
                    tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                self.body.blit(tower_img, self.tower_rects[i])
                temp_rect = self.tower_rects[i].copy()
                temp_rect.x += self.tower_size + self.offset
                self.body.blit(PROTEIN_IMG, temp_rect)
                cost_text = self.font.render(str(round(TOWER_DATA[tower]["stages"][0]["upgrade_cost"] * (1 + self.game.difficulty * 0.25))), 1, WHITE)
                temp_rect.y += HEART_IMG.get_size()[0]
                self.body.blit(cost_text, temp_rect)

        else:
            tower_dat = TOWER_DATA[self.tower.name]
            tower_img = pg.transform.scale(tower_dat["stages"][self.tower.stage]["image"], (self.width - MENU_OFFSET * 2, self.width - MENU_OFFSET * 2))
            self.body.blit(tower_img, self.tower_rects[0])

            font = pg.font.Font(FONT, int(HEART_IMG.get_size()[0] * 1.3))
            text = font.render("Damage: " + str(tower_dat["stages"][self.tower.stage]["damage"]), 1, WHITE)
            self.body.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height()))

            text = font.render("Speed: " + str(tower_dat["stages"][self.tower.stage]["attack_speed"]) + "s", 1, WHITE)
            self.body.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + text.get_height()))

            text = font.render("Hits: " + str(self.tower.hits), 1, WHITE)
            self.body.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + text.get_height() * 2))

            text = font.render("Kills: " + str(self.tower.kills), 1, WHITE)
            self.body.blit(text, (MENU_OFFSET, self.tower_rects[0].top + tower_img.get_height() + text.get_height() * 3))

            refund = 0
            for stage in range(self.tower.stage + 1):
                refund += round(tower_dat["stages"][stage]["upgrade_cost"] * (1 + self.game.difficulty * 0.25) / 2)
            sell_button, self.sell_rect = self.make_button("Sell: " + str(refund), True)
            self.sell_rect.bottom = self.body.get_height()
            self.body.blit(sell_button, self.sell_rect)

            if self.tower.stage < 2:
                upgrade_cost = round(tower_dat["stages"][self.tower.stage + 1]["upgrade_cost"] * (1 + self.game.difficulty * 0.25))
                upgrade_button, self.upgrade_rect = self.make_button("Upgrade: " + str(upgrade_cost), self.game.protein >= upgrade_cost)
                self.upgrade_rect.bottom = self.sell_rect.bottom - self.sell_rect.height - self.offset
                self.body.blit(upgrade_button, self.upgrade_rect)

            if not self.tower.area_of_effect:
                target_button, self.target_rect = self.make_button("Target: " + TARGET_OPTIONS[self.tower.targeting_option], True)
                if self.tower.stage == 2:
                    self.target_rect.bottom = self.sell_rect.bottom - self.sell_rect.height - self.offset
                else:
                    self.target_rect.bottom = self.upgrade_rect.bottom - self.upgrade_rect.height - self.offset
                self.body.blit(target_button, self.target_rect)

    def generate_next_wave(self):
        self.next_wave.fill(DARK_GREY)
        text = "Next Wave"
        if self.game.wave < 0:
            text = "Start Wave"

        next_wave_button, self.next_wave_rect = self.make_button(text, self.next_wave_btn_enabled)
        self.next_wave_rect.top = self.offset
        self.next_wave.blit(next_wave_button, self.next_wave_rect)

        if self.game.wave > 0:
            timer_width = (self.width - MENU_OFFSET * 2) * (WAVE_DELAY * 1000 - self.game.time_passed) // (WAVE_DELAY * 1000)
            pg.draw.rect(self.next_wave, GREEN, pg.Rect(self.offset, 0, timer_width, self.offset))

        self.next_wave_rect.bottom = self.ui.get_height() - self.offset - self.header.get_height()

    def get_ui(self):
        self.ui.blit(self.header, (0, 0))
        self.ui.blit(self.body, self.body.get_rect(top=self.header.get_height()))
        self.ui.blit(self.next_wave, self.next_wave.get_rect(bottom = self.ui.get_height()))

    def make_button(self, string, enabled):
        font = pg.font.Font(FONT, int(HEART_IMG.get_size()[0] * 1.3))
        text = font.render(string, 1, WHITE)
        btn = pg.transform.scale(LEVEL_BUTTON_IMG, (self.width - self.offset * 2,
                                                              text.get_height())).copy().convert_alpha()
        btn.blit(text, text.get_rect(center=btn.get_rect().center))

        if not enabled:
            btn.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)

        rect = btn.get_rect()
        rect.left = MENU_OFFSET

        return btn, rect

    def event(self, pos):
        pos = (pos[0], pos[1] - self.header.get_height())
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

            elif not self.tower.area_of_effect and self.target_rect.collidepoint(pos):
                return "target"

        if self.next_wave_btn_enabled and self.next_wave_rect.collidepoint(pos):
            return "start_wave"

        return -1

class Textbox(pg.Surface):
    def __init__(self, game):
        self.game = game
        self.enabled = False
        self.writing = False
        self.rect = pg.Rect(0, 0, SCREEN_WIDTH - MENU_OFFSET * 2, 0)
        self.set_text("")
        self.yoffset = 0
        self.draw()

    def update(self):
        if self.enabled and self.yoffset > 0:
            self.yoffset -= 10
            return

        elif not self.enabled and self.yoffset < self.rect.height + MENU_OFFSET:
            self.yoffset += 10
            return

        elif self.position < len(self.text):
            self.position += 2
            self.current_text = self.text[:self.position]
            
            if (self.position - 1) % 6 == 0: # Plays text scroll sfx every 3 updates
                TEXT_SCROLL_SFX.play()
            self.draw()

        elif self.writing:
            self.writing = False

    def toggle(self, state):
        if state:
            self.enabled = True
        else:
            self.enabled = False
            self.game.text = False
            self.game.prepare_next_wave()

    def draw(self):
        height = MENU_OFFSET
        self.font = pg.font.Font(FONT, MENU_TEXT_SIZE * 2)
        text = textwrap.fill(self.current_text, 57)  # No idea how to really calculate this.
        text = text.split("\n")
        texts = []
        for i, part in enumerate(text):
            rendered_text = self.font.render(part, 1, WHITE)
            texts.append(rendered_text)
            height += MENU_TEXT_SIZE * 2

        self.rect.height = height + MENU_OFFSET
        super().__init__((self.rect.width, self.rect.height))
        temp_img = pg.transform.scale(LEVEL_BUTTON_IMG, (self.rect.width, self.rect.height))
        self.blit(temp_img, (0, 0))
        height = MENU_OFFSET
        for text in texts:
            self.blit(text, (MENU_OFFSET, height))
            height += MENU_TEXT_SIZE * 2

    def set_text(self, text):
        self.text = text
        self.current_text = ""
        self.position = 1
        self.writing = True

    def finish_text(self):
        self.current_text = self.text
        self.position = len(self.text)
        self.writing = False
        self.draw()
        self.yoffset = 0

    def fast_forward(self):
        if self.enabled and not self.writing and self.yoffset < self.rect.height:
            self.yoffset = self.rect.height
            return

        elif not self.enabled and self.yoffset > 0:
            self.yoffset = 0
            return

        self.finish_text()

class Explosion(pg.sprite.Sprite):
    def __init__(self, game, x, y, rad, color = 0):
        super().__init__(game.explosions)
        self.clock = game.clock
        self.x = x - rad / 2
        self.y = y - rad / 2
        self.rad = rad
        self.state = 0
        self.color = AURA_COLORS[color]
        self.surf = pg.Surface((rad, rad)).convert_alpha()

    def update(self):
        passed_time = self.clock.get_time() / 1000
        self.state += passed_time / EXPLOSION_TIME
        if self.state >= 1:
            self.kill()
        else:
            self.surf.fill(pg.Color(self.color.r, self.color.g, self.color.b, round(127 * self.state)))

    def get_surf(self):
        return self.surf

class NewEnemyBox(pg.Surface):
    def __init__(self):
        self.enabled = False
        self.show = False
        self.enemy = None
        self.opacity = 0
        self.rect = pg.Rect(MENU_OFFSET * 9, MENU_OFFSET * 9, SCREEN_WIDTH - MENU_OFFSET * 18, SCREEN_HEIGHT - MENU_OFFSET * 18)
        super().__init__(self.rect.size)

    def get_surf(self):
        self.convert_alpha()
        self.set_alpha(self.opacity)
        return self

    def draw(self):
        enemy_dat = ENEMY_DATA[self.enemy]
        self.blit(pg.transform.scale(LEVEL_BUTTON_IMG, self.rect.size), (0, 0))

        big_font = pg.font.Font(FONT, MENU_TEXT_SIZE * 4)
        title = big_font.render("A NEW ENEMY APPEARS!", 1, WHITE)
        self.blit(title, title.get_rect(center = (self.rect.width / 2, MENU_OFFSET * 7)))

        enemy_image = pg.transform.scale(enemy_dat["image"], (300, 300))
        self.blit(enemy_image, enemy_image.get_rect(bottomleft = (MENU_OFFSET * 2, self.rect.height - MENU_OFFSET * 6)))

        texts = []
        texts.append([("Name: " + self.enemy.replace("_", " ").title(), WHITE)])
        if "shield_hp" in enemy_dat:
            texts.append([("HP: ", WHITE), (str(enemy_dat["hp"]), GREEN), (" +" + str(enemy_dat["shield_hp"]), CYAN)])
        else:
            texts.append([("HP: ", WHITE), (str(enemy_dat["hp"]), GREEN)])
        texts.append([("Speed: " + str(enemy_dat["speed"]), WHITE)])
        abilities = [("Abilities: ", WHITE)]
        if enemy_dat["flying"]:
            abilities.append(("Fly, ", GREEN))
        if enemy_dat["mutate"]:
            abilities.append(("Mutate, ", DARK_GREEN))
        if enemy_dat["explode_on_death"]:
            abilities.append(("Explode, ", YELLOW))

        if len(abilities) == 1:
            abilities.append(("None", WHITE))

        else:
            abilities[-1] = (abilities[-1][0][:-2], abilities[-1][1])

        texts.append(abilities)

        font = pg.font.Font(FONT, MENU_TEXT_SIZE * 3)
        height = title.get_height()
        for line in texts:
            width = enemy_image.get_width() + MENU_OFFSET * 4
            for text, color in line:
                text_img = font.render(text, 1, color)
                self.blit(text_img, text_img.get_rect(topleft = (width, height)))
                width += text_img.get_width()
            height += text_img.get_height() + MENU_OFFSET

    def show_new_enemy(self, enemy):
        self.enemy = enemy
        self.show = True
        self.enabled = True
        self.draw()

    def update(self):
        if self.enabled and self.opacity < 255:
            self.opacity += 51

        elif not self.enabled:
            if self.opacity > 0:
                self.opacity -= 51
            else:
                self.show = False
