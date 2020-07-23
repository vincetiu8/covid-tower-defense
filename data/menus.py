import textwrap, math

from data.display import *
from data.tilemap import Camera, TiledMap
from data.settings import *
from data.game_stop import GridDisplay

class StartMenu(GridDisplay):
    def __init__(self, clock):
        super().__init__()
        self.clock = clock
        self.fade_out_done_event = pg.event.Event(pg.USEREVENT + 2)
        self.fading_out = False
        self.alpha_speed = 25
        self.text_alpha_speed = 10
        self.fonts = [pg.font.Font(FONT, 100), pg.font.Font(FONT, 200)]
        self.init_text([("In light of COVID-19", 0), ("Made by the BSM community", 0), ("With thanks to frontliners", 0)])

        self.half_distances = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

        # For enemy images
        self.enemy_pos = [(300, 550), (400, 500), (200, 450)]
        self.raw_enemies = [
            pg.transform.scale(ENEMY_DATA[enemy]["image"], (
                    ENEMY_DATA[enemy]["image"].get_width() * 10,
                    ENEMY_DATA[enemy]["image"].get_height() * 10
            ))
            for enemy in ["common_cold", "hepatitis_b", "hiv"]]
        self.processed_enemies = []
        self.enemy_bob = 0

        # For tower images
        self.tower_pos = [(1000, 550), (900, 475), (1100, 400)]
        self.raw_tower_bases = [
            pg.transform.scale(TOWER_DATA[tower]["stages"][stage]["base_image"], (
                    TOWER_DATA[tower]["stages"][stage]["base_image"].get_width() * 5,
                    TOWER_DATA[tower]["stages"][stage]["base_image"].get_height() * 5
            )) for stage, tower in enumerate(["t_cell", "m_cell", "b_cell"])]
        self.raw_tower_guns = [
            pg.transform.scale(TOWER_DATA[tower]["stages"][stage]["gun_image"], (
                    TOWER_DATA[tower]["stages"][stage]["gun_image"].get_width() * 5,
                    TOWER_DATA[tower]["stages"][stage]["gun_image"].get_height() * 5
            )) for stage, tower in enumerate(["t_cell", "m_cell", "b_cell"])]
        self.processed_tower_guns = [{}, {}, {}]
        self.tower_rot = 0

        self.vs_img_h = 475
        self.vs_img_bob = 0

        self.start_text = self.render_text("Press ANY KEY to start", self.fonts[0], WHITE, BLACK)
        self.start_text_h = 650

        self.stage = 0
        self.text_stage = 1
        self.text_alpha = 0

    def new(self, args):
        super().new(args)

        pg.mixer.music.stop()
        pg.mixer.music.load(SEVERE_LEVEL_MUSIC[1])
        pg.mixer.music.play(0)  # have to make the song play 0 times for some reason...
        pg.mixer.music.set_endevent(pg.USEREVENT + 3)

    def init_text(self, texts):
        self.raw_texts = []
        for text, size in texts:
            temp_text = self.render_text(text, self.fonts[size], WHITE, BLACK)
            self.raw_texts.append(temp_text)

    def draw_text(self):
        if self.alpha > 255:
            return

        if self.stage == 0:
            if self.text_alpha < 255:
                self.text_alpha = min(255, self.text_alpha + self.text_alpha_speed)

            elif self.text_stage < len(self.raw_texts):
                self.text_stage += 1
                self.text_alpha = 0

            else:
                self.stage += 1

            for stage in range(self.text_stage):
                text = self.raw_texts[stage]
                if stage == self.text_stage - 1:
                    text = text.copy()
                    text.fill(pg.Color(255, 255, 255, self.text_alpha), special_flags = pg.BLEND_RGBA_MULT)
                self.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, (SCREEN_HEIGHT - text.get_height()) * (stage + 1) // 4))

        elif self.stage == 1:
            if self.text_alpha > 0:
                self.text_alpha = max(0, self.text_alpha - self.text_alpha_speed)

            else:
                self.init_text([("Sergeant T-Cell", 1), ("and the", 0), ("Abnormally Impressive", 0), ("Invasion of Illnesses", 0)])
                self.final_pos = [
                    self.half_distances[1] - self.raw_texts[0].get_height()
                    - self.raw_texts[1].get_height() - MENU_OFFSET * 7,
                    self.half_distances[0]
                    - (self.raw_texts[1].get_width() + self.raw_texts[2].get_width() + MENU_OFFSET * 2) / 2,
                    self.half_distances[0]
                    - (self.raw_texts[2].get_width() - self.raw_texts[1].get_width() - MENU_OFFSET * 2) / 2,
                    self.half_distances[1] + self.raw_texts[1].get_height() - MENU_OFFSET * 5
                ]
                self.text_stage = 0
                self.text_alpha = 0
                self.stage += 1

            for stage, text in enumerate(self.raw_texts):
                text = text.copy()
                text.fill(pg.Color(255, 255, 255, self.text_alpha), special_flags=pg.BLEND_RGBA_MULT)
                self.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, (SCREEN_HEIGHT - text.get_height()) * (stage + 1) // 4))

        elif self.stage == 2:
            if self.text_alpha < 100:
                self.text_alpha = min(100, self.text_alpha + self.text_alpha_speed)

            elif self.text_stage < len(self.raw_texts):
                self.text_stage += 1
                self.text_alpha = 0

            else:
                self.stage += 1
                self.text_alpha = 0
                self.text_stage = 0

            for stage in range(self.text_stage):
                text = self.raw_texts[stage]
                multiplier = 1
                if stage == self.text_stage - 1:
                    multiplier = self.text_alpha / 100

                if stage % 3 == 0:
                    final_x = self.half_distances[0] - text.get_width() / 2
                    if stage == 0:
                        final_y = (text.get_height() + self.final_pos[stage] - MENU_OFFSET * stage * 12) * multiplier - text.get_height()
                    else:
                        final_y = (self.final_pos[stage] - MENU_OFFSET * stage * 6 - SCREEN_HEIGHT) * multiplier + SCREEN_HEIGHT

                else:
                    final_y = self.half_distances[1] - text.get_height() / 2 - MENU_OFFSET * 16
                    if stage == 1:
                        final_x = (self.final_pos[stage] + text.get_width()) * multiplier - text.get_width()
                    else:
                        final_x = (self.final_pos[stage] - SCREEN_WIDTH) * multiplier + SCREEN_WIDTH

                self.blit(text, (final_x, final_y))

        elif self.stage == 3:
            if self.text_alpha < 100:
                self.text_alpha = min(100, self.text_alpha + self.text_alpha_speed)

            elif self.text_stage < len(self.raw_enemies):
                self.text_stage += 1
                self.text_alpha = 0

            else:
                self.stage += 1
                self.text_alpha = 0
                self.text_stage = 0
            
            for stage in range(self.text_stage - 1, -1, -1):
                if stage == self.text_stage - 1:
                    size = self.raw_enemies[stage].get_width() * self.text_alpha // 100
                    temp_img = pg.transform.scale(self.raw_enemies[stage], (size, size))
                    if self.text_alpha == 100:
                        self.processed_enemies.append({size: temp_img})
                    self.blit(temp_img, temp_img.get_rect(center = self.enemy_pos[stage]))

                else:
                    self.blit(self.raw_enemies[stage], self.raw_enemies[stage].get_rect(center = self.enemy_pos[stage]))

            self.draw_title_text()

        elif self.stage == 4:
            self.tower_rot += 3

            if self.text_alpha < 100:
                self.text_alpha = min(100, self.text_alpha + self.text_alpha_speed)

            elif self.text_stage < len(self.raw_tower_bases):
                self.text_alpha = 0
                self.text_stage += 1

            else:
                self.text_alpha = 10
                self.stage += 1

            for stage in range(self.text_stage - 1, -1, -1):
                angle = self.tower_rot // (stage + 1) * (stage % 2 * 2 - 1)
                if stage == self.text_stage - 1:
                    size = self.raw_tower_bases[stage].get_width() * self.text_alpha // 100
                    temp_img = pg.transform.scale(self.raw_tower_bases[stage], (size, size))
                    self.blit(temp_img, temp_img.get_rect(center = self.tower_pos[stage]))
                    temp_img = pg.transform.scale(pg.transform.rotate(self.raw_tower_guns[stage], angle), (
                        self.raw_tower_guns[stage].get_width() * self.text_alpha // 100,
                        self.raw_tower_guns[stage].get_height() * self.text_alpha // 100
                    ))
                    self.blit(temp_img, temp_img.get_rect(center=self.tower_pos[stage]))

                else:
                    self.blit(self.raw_tower_bases[stage], self.raw_tower_bases[stage].get_rect(center = self.tower_pos[stage]))
                    if angle in self.processed_tower_guns[stage]:
                        temp_img = self.processed_tower_guns[stage][angle]
                    else:
                        temp_img = pg.transform.rotate(self.raw_tower_guns[stage], angle)
                        self.processed_tower_guns[stage][angle] = temp_img
                    self.blit(temp_img, temp_img.get_rect(center = self.tower_pos[stage]))

            self.draw_enemies()
            self.draw_title_text()

        elif self.stage == 5:
            if self.text_alpha > 1:
                self.text_alpha = max(1, self.text_alpha - 0.5)

            else:
                self.stage += 1
                self.text_alpha = 0

            temp_img = pg.transform.scale(VS_IMG, (round(VS_IMG.get_width() * self.text_alpha), round(VS_IMG.get_height() * self.text_alpha)))
            self.blit(temp_img, temp_img.get_rect(center = (self.half_distances[0], self.vs_img_h)))

            self.draw_towers()
            self.draw_enemies()
            self.draw_title_text()

        elif self.stage == 6:
            if self.text_alpha < 255:
                self.text_alpha = min(255, self.text_alpha + self.text_alpha_speed // 4)

            self.draw_vs()
            self.draw_towers()
            self.draw_enemies()
            self.draw_title_text()

            text = self.start_text.copy()
            text.fill(pg.Color(255, 255, 255, self.text_alpha), special_flags = pg.BLEND_RGBA_MULT)
            self.blit(text, text.get_rect(center = (self.half_distances[0], self.start_text_h)))

    def draw_vs(self):
        self.vs_img_bob += 1
        self.blit(VS_IMG, VS_IMG.get_rect(center=(self.half_distances[0], self.vs_img_h + round(25 * math.sin(math.radians(self.vs_img_bob))))))

    def draw_towers(self):
        self.tower_rot += 3

        for stage in range(len(self.raw_tower_bases) - 1, -1, -1):
            angle = self.tower_rot // (stage + 1) * (stage % 2 * 2 - 1)
            self.blit(self.raw_tower_bases[stage], self.raw_tower_bases[stage].get_rect(center=self.tower_pos[stage]))
            if angle in self.processed_tower_guns[stage]:
                temp_img = self.processed_tower_guns[stage][angle]
            else:
                temp_img = pg.transform.rotate(self.raw_tower_guns[stage], angle)
                self.processed_tower_guns[stage][angle] = temp_img
            self.blit(temp_img, temp_img.get_rect(center=self.tower_pos[stage]))

    def draw_enemies(self):
        self.enemy_bob += 1

        for stage in range(len(self.raw_enemies) - 1, -1, -1):
            size = round((math.sin(self.enemy_bob / (stage / 2 + 1) / 10 / math.pi) / 10 + 1) * self.raw_enemies[stage].get_width())
            if size not in self.processed_enemies[stage]:
                temp_img = pg.transform.scale(self.raw_enemies[stage], (size, size))
                self.processed_enemies[stage][size] = temp_img
                self.blit(temp_img, temp_img.get_rect(center = self.enemy_pos[stage]))

            else:
                self.blit(self.processed_enemies[stage][size], self.processed_enemies[stage][size].get_rect(center=self.enemy_pos[stage]))

    def draw_title_text(self):
        for stage, text in enumerate(self.raw_texts):
            if stage % 3 == 0:
                final_x = self.half_distances[0] - text.get_width() / 2
                final_y = self.final_pos[stage] - MENU_OFFSET * stage * 6

            else:
                final_y = self.half_distances[1] - text.get_height() / 2 - MENU_OFFSET * 16
                final_x = self.final_pos[stage]

            self.blit(text, (final_x, final_y))

    def draw(self):
        self.game_stop_surf.fill(BLACK)
        if self.fading_out:
            self.alpha = max(0, self.alpha - self.alpha_speed)
            if self.alpha == 0:
                pg.event.post(self.fade_out_done_event)
                self.fading_out = False
        else:
            self.alpha = min(255, self.alpha + self.alpha_speed)

        self.draw_grid()
        super().draw()
        self.draw_text()
        return self

    def event(self, event):
        if event.type == pg.KEYDOWN:
            return "menu"

        elif event.type == pg.USEREVENT + 3: # skip the intro part of the late severe song when looping
            pg.mixer.music.load(LATE_SEVERE_MUSIC_LOOP)
            pg.mixer.music.play(-1)
            pg.mixer.music.set_endevent()

        return -1

class Menu(Display):
    def __init__(self):
        super().__init__((SAVE_DATA["width"], SAVE_DATA["height"]))
        self.camera = Camera(SAVE_DATA["width"] * 0.8, SAVE_DATA["height"] * 0.8, SAVE_DATA["width"], SAVE_DATA["height"], 1.5)
        
        self.base_zoom = self.camera.get_zoom()
        self.zoom_step = -1
        self.body_images = []
        self.body_image = self.camera.apply_image(BODY_IMG)
        
        self.body_coords = (-150, 400)
        
        self.level_button_rect = LEVEL_BUTTON_IMG.get_rect()
        self.level_button_rect_2 = LEVEL_BUTTON_IMG_2.get_rect()
        self.small_level_button_size = (int(self.level_button_rect.size[0] * 0.6), int(self.level_button_rect.size[1] * 0.6))
        self.small_level_button_img = pg.transform.scale(LEVEL_BUTTON_IMG, self.small_level_button_size)
        self.level_buttons = []
        self.init_levels()

        self.tower_preview_button = pg.Rect((850, 300), self.level_button_rect.size)
        self.enemy_preview_button = pg.Rect((850, 670), self.level_button_rect.size)
        self.upgrades_menu_button = pg.Rect((850, 1040), self.level_button_rect.size)
        self.tower_edit_button = pg.Rect((1150, 300), self.level_button_rect.size)
        self.enemy_edit_button = pg.Rect((1150, 670), self.level_button_rect.size)
        self.level_edit_button = pg.Rect((1150, 1040), self.level_button_rect.size)
        self.options_button = pg.Rect((840, 30), OPTIONS_IMGS[0].get_size())
        self.plus_button = pg.Rect((650, 250), self.small_level_button_size)
        self.minus_button = pg.Rect((0, 250), self.small_level_button_size)
        
        self.difficulty = 0
        
        self.init_body_1()
        
    def init_levels(self):
        for i, level in enumerate(LEVEL_DATA):
            temp_coords = BODY_PARTS[list(BODY_PARTS)[level["body_part"]]]
            true_coords = (temp_coords[0] + self.body_coords[0] - self.level_button_rect_2.w // 2,
                           temp_coords[1] + self.body_coords[1] - self.level_button_rect_2.h // 2)
            self.level_buttons.append(pg.Rect(true_coords, self.level_button_rect_2.size))
        
    def init_body_1(self): #inits half the body_images on game startup
        for i in range(4):
            self.camera.zoom(ZOOM_AMT_MENU)
            self.body_images.append(self.camera.apply_image(BODY_IMG))
        self.camera.zoom(self.base_zoom - self.camera.get_zoom())
        
    def new(self, args): #inits the other half of the body images
        self.level_infos = [[None for j in range(3)] for i in range(len(LEVEL_DATA))]
        self.over_level = -1
        self.hover_options = False
        
        if args[0]: # prev display is game, pause, or game_over
            pg.mixer.music.stop()
            pg.mixer.music.load(MENU_MUSIC)
            pg.mixer.music.play(-1)

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.camera.move(25, 0)

        elif keys[pg.K_RIGHT]:
            self.camera.move(-25, 0)

        elif keys[pg.K_UP]:
            self.camera.move(0, 25)

        elif keys[pg.K_DOWN]:
            self.camera.move(0, -25)

    def draw(self):
        temp_surf = pg.Surface((1350, 1350)) # set surface width to 1100 when removing the edit buttons

        big_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w * 3)
        lives_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w)
        level_text = big_font.render("Levels", 1, WHITE)
        temp_surf.blit(level_text, (20, -100))
        
        temp_surf.blit(OPTIONS_IMGS[self.hover_options], self.options_button)

        if len(SAVE_DATA["seen_enemies"]) == 0:
            temp_surf.blit(DARK_LEVEL_BUTTON_IMG, self.tower_preview_button)
        else:
            temp_surf.blit(LEVEL_BUTTON_IMG, self.tower_preview_button)

        lives_text = lives_font.render("Tower", 1, WHITE)
        temp_surf.blit(lives_text,
                        (self.tower_preview_button.center[0] - lives_text.get_rect().center[0],
                        self.tower_preview_button.center[1] - lives_text.get_rect().center[
                        1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Preview", 1, WHITE)
        temp_surf.blit(lives_text,
                       (self.tower_preview_button.center[0] - lives_text.get_rect().center[0],
                        self.tower_preview_button.center[1] - lives_text.get_rect().center[
                        1] + lives_text.get_rect().height - MENU_OFFSET))

        if len(SAVE_DATA["seen_enemies"]) == 0:
            temp_surf.blit(DARK_LEVEL_BUTTON_IMG, self.enemy_preview_button)
        else:
            temp_surf.blit(LEVEL_BUTTON_IMG, self.enemy_preview_button)
            
        lives_text = lives_font.render("Enemy", 1, WHITE)
        temp_surf.blit(lives_text,
                       (self.enemy_preview_button.center[0] - lives_text.get_rect().center[0],
                        self.enemy_preview_button.center[1] - lives_text.get_rect().center[
                        1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Preview", 1, WHITE)
        temp_surf.blit(lives_text,
                       (self.enemy_preview_button.center[0] - lives_text.get_rect().center[0],
                        self.enemy_preview_button.center[1] - lives_text.get_rect().center[
                        1] + lives_text.get_rect().height - MENU_OFFSET))

        temp_surf.blit(LEVEL_BUTTON_IMG, self.upgrades_menu_button)
        lives_text = lives_font.render("Upgrades", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.upgrades_menu_button.center[0] - lives_text.get_rect().center[0],
             self.upgrades_menu_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Menu", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.upgrades_menu_button.center[0] - lives_text.get_rect().center[0],
             self.upgrades_menu_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET))

        temp_surf.blit(LEVEL_BUTTON_IMG, self.tower_edit_button)
        lives_text = lives_font.render("Tower", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.tower_edit_button.center[0] - lives_text.get_rect().center[0], self.tower_edit_button.center[1] - lives_text.get_rect().center[1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Edit", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.tower_edit_button.center[0] - lives_text.get_rect().center[0], self.tower_edit_button.center[1] - lives_text.get_rect().center[1] + lives_text.get_rect().height - MENU_OFFSET))

        temp_surf.blit(LEVEL_BUTTON_IMG, self.enemy_edit_button)
        lives_text = lives_font.render("Enemy", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.enemy_edit_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_edit_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Edit", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.enemy_edit_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_edit_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET))

        temp_surf.blit(LEVEL_BUTTON_IMG, self.level_edit_button)
        lives_text = lives_font.render("Level", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.level_edit_button.center[0] - lives_text.get_rect().center[0],
             self.level_edit_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET))
        lives_text = lives_font.render("Edit", 1, WHITE)
        temp_surf.blit(lives_text,
            (self.level_edit_button.center[0] - lives_text.get_rect().center[0],
             self.level_edit_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET))
        
        minus_plus_font = pg.font.Font(FONT, 110)
        difficulty_font = pg.font.Font(FONT, 100)
        
        difficulties = ["Mild", "Acute", "Severe"]
        difficulty_text = difficulty_font.render("Difficulty: {}".format(difficulties[self.difficulty]), 1, WHITE)
        difficulty_x = (self.minus_button.topleft[0] + self.plus_button.topright[0] - difficulty_text.get_width()) // 2
        temp_surf.blit(difficulty_text, (difficulty_x, self.minus_button.y - 10))
        
        if self.difficulty > 0:
            minus_btn = self.small_level_button_img.copy()
            minus_text = minus_plus_font.render("-", 1, WHITE)
            minus_btn.blit(minus_text, minus_text.get_rect(center = minus_btn.get_rect().center))
            temp_surf.blit(minus_btn, self.minus_button)

        if self.difficulty < 2:
            plus_btn = self.small_level_button_img.copy()
            plus_text = minus_plus_font.render("+", 1, WHITE)
            plus_btn.blit(plus_text, plus_text.get_rect(center = plus_btn.get_rect().center))

            if SAVE_DATA["latest_level_unlocked"][self.difficulty + 1] == -1:
                plus_btn.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)
                
            temp_surf.blit(plus_btn, self.plus_button)

        self.fill(BLACK)
        self.blit(self.camera.apply_image(temp_surf), self.camera.apply_tuple((0, 0)))
        self.draw_body()
        
        return self
    
    def draw_body(self):
        self.blit(self.body_image, self.camera.apply_tuple(self.body_coords))
        for i, button in enumerate(self.level_buttons):
            button_tuple = (button.x, button.y)
            if SAVE_DATA["latest_level_unlocked"][self.difficulty] >= i:
                if SAVE_DATA["latest_level_completed"][self.difficulty] >= i:
                    green_image = LEVEL_BUTTON_IMG_2.copy().convert_alpha()
                    green_image.fill(BLACK, special_flags = pg.BLEND_RGB_MULT)
                    green_image.fill(GREEN, special_flags = pg.BLEND_RGB_MAX)
                    self.blit(self.camera.apply_image(green_image), self.camera.apply_tuple(button_tuple))
                else:
                    self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG_2), self.camera.apply_tuple(button_tuple))
            else:
                grey_image = LEVEL_BUTTON_IMG_2.copy()
                grey_image.fill(DARK_GREY, special_flags=pg.BLEND_RGB_MIN)
                self.blit(self.camera.apply_image(grey_image), self.camera.apply_tuple(button_tuple))
        
        if self.over_level != -1:
            if self.level_infos[self.over_level][self.difficulty] == None:
                new_level_info = LevelInfo(self.over_level, self.difficulty)
                self.level_infos[self.over_level][self.difficulty] = new_level_info.draw()
                
            level_info = self.level_infos[self.over_level][self.difficulty]
            if self.level_buttons[self.over_level].centerx < self.get_width() / 2:
                self.blit(self.camera.apply_image(level_info), self.camera.apply_tuple(self.level_buttons[self.over_level].topright))
            else:
                self.blit(self.camera.apply_image(level_info), self.camera.apply_tuple(level_info.get_rect(topright = self.level_buttons[self.over_level].topleft)))

    def update_level(self, mouse_pos):
        for i, button in enumerate(self.level_buttons):
            if button.collidepoint(mouse_pos):
                self.over_level = i
                return
            
        self.over_level = -1

    def get_over_level(self):
        return self.over_level
    
    def get_difficulty(self):
        return self.difficulty
    
    def update_body_img(self):
        if self.zoom_step >= 0:
            self.body_image = self.body_images[self.zoom_step]
        else:
            self.body_image = self.camera.apply_image(BODY_IMG)

    def scale_tuple(self, tuple, scale):
        return (int(tuple[0] * scale), int(tuple[1] * scale))
    
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = self.camera.correct_mouse(event.pos)
                if self.tower_preview_button.collidepoint(mouse_pos):
                    if len(SAVE_DATA["seen_enemies"]) > 0:
                        BTN_SFX.play()
                        return "tower_preview"
                    else:
                        WRONG_SELECTION_SFX.play()
                        
                elif self.enemy_preview_button.collidepoint(mouse_pos):
                    if len(SAVE_DATA["seen_enemies"]) > 0:
                        BTN_SFX.play()
                        return "enemy_preview"
                    else:
                        WRONG_SELECTION_SFX.play()
                elif self.upgrades_menu_button.collidepoint((mouse_pos)):
                    BTN_SFX.play()
                    return "upgrades_menu"
                elif self.tower_edit_button.collidepoint(mouse_pos):
                    BTN_SFX.play()
                    return "tower_edit"
                elif self.enemy_edit_button.collidepoint(mouse_pos):
                    BTN_SFX.play()
                    return "enemy_edit"
                elif self.level_edit_button.collidepoint(mouse_pos):
                    BTN_SFX.play()
                    return "level_edit"
                elif self.options_button.collidepoint(mouse_pos):
                    BTN_SFX.play()
                    return "options"
                if self.difficulty > 0 and self.minus_button.collidepoint(mouse_pos):
                    BTN_2_SFX.play()
                    self.difficulty -= 1
                elif self.difficulty < 2 and self.plus_button.collidepoint(mouse_pos):
                    if SAVE_DATA["latest_level_unlocked"][self.difficulty + 1] > -1:
                        BTN_2_SFX.play()
                        self.difficulty += 1
                    else:
                        WRONG_SELECTION_SFX.play()
                
                if self.over_level != -1:
                    if self.over_level <= SAVE_DATA["latest_level_unlocked"][self.difficulty]:
                        BTN_SFX.play()
                        return "tower_select"
                    else:
                        WRONG_SELECTION_SFX.play()

            elif event.button == 4:
                if self.camera.zoom(ZOOM_AMT_MENU) != False:
                    self.zoom_step += 1
                    self.update_body_img()

            elif event.button == 5:
                if self.camera.zoom(-ZOOM_AMT_MENU) != False:
                    self.zoom_step -= 1
                    self.update_body_img()

        elif event.type == pg.MOUSEMOTION:
            mouse_pos = self.camera.correct_mouse(event.pos)
            self.update_level(mouse_pos)

            if self.options_button.collidepoint(mouse_pos):
                self.hover_options = True
            else:
                self.hover_options = False

        return -1

class TowerMenu(Display):
    def __init__(self):
        super().__init__()

    def get_dims(self):
        return (GRID_CELL_SIZE, GRID_CELL_SIZE)

    def get_locs(self, row, col):
        x = GRID_MARGIN_X + col * (GRID_CELL_SIZE + GRID_SEPARATION)
        y = GRID_MARGIN_Y + row * (GRID_CELL_SIZE + GRID_SEPARATION)

        return (x, y)

    def make_btn(self, string):
        font = pg.font.Font(FONT, 70)
        text = font.render(string, 1, WHITE)
        btn = pg.transform.scale(LEVEL_BUTTON_IMG,
                                 (text.get_width() + BTN_PADDING * 2, text.get_height())).copy().convert_alpha()
        btn.blit(text, text.get_rect(center=btn.get_rect().center))
        return btn

class TowerSelectMenu(TowerMenu):
    def __init__(self):
        super().__init__()
        self.start_btn = self.make_btn("Start")
        self.back_btn = self.make_btn("Back")
        self.start_btn_rect = pg.Rect(SCREEN_WIDTH - BTN_X_MARGIN - self.start_btn.get_width(),
                                      BTN_Y, self.start_btn.get_width(), self.start_btn.get_height())
        self.back_btn_rect = pg.Rect(BTN_X_MARGIN, BTN_Y, self.back_btn.get_width(), self.back_btn.get_height())
        
        self.start_btn_disabled = self.make_btn("Start")
        self.start_btn_disabled.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)
        
        self.left_btn_rect = None
        self.right_btn_rect = None
        
    def new(self, args):
        # args[0] = level
        self.level_data = LEVEL_DATA[args[0]]
        map = TiledMap(path.join(MAP_FOLDER, "{}.tmx".format(list(BODY_PARTS)[LEVEL_DATA[args[0]]["body_part"]])))
        self.map_img = None
        self.draw_map(map)

        self.difficulty = args[1]
        self.towers = []
        self.tower_rects = []
        self.tower_selected = []

        self.over_tower = [-1, -1]
        self.num_selected = 0

        tower_names = SAVE_DATA["owned_towers"]

        row = -1
        for i in range(len(tower_names)):
            if i % GRID_ROW_SIZE == 0:
                row += 1
                self.towers.append([])
                self.tower_rects.append([])
                self.tower_selected.append([])

            self.towers[row].append(tower_names[i])
            self.tower_rects[row].append(pg.Rect(self.get_locs(row, i % GRID_ROW_SIZE), self.get_dims()))
            self.tower_selected[row].append(False)

        self.tower_infos = [None for i in range(len(tower_names))]
        self.enemy_infos = {}

        self.load_level_data()

    def load_level_data(self):
        self.max_wave = len(self.level_data["waves"][self.difficulty])
        self.curr_wave = 0
        self.wave_info = None
        self.over_enemy = None
        self.wave_data = {}
        
    def draw(self):
        self.fill(BLACK)
        
        title_font = pg.font.Font(FONT, 120)
        text_font = pg.font.Font(FONT, 70)
        
        # Draws upper left text
        title_1 = title_font.render("Select Towers", 1, WHITE)
        selected_text = text_font.render("Selected: {}/{}".format(self.num_selected, SAVE_DATA["game_attrs"]["max_towers"]["value"]), 1, WHITE)
        
        self.blit(title_1, (SCREEN_WIDTH / 4 - title_1.get_width() / 2, 0)) # puts these on the x center of the screnn's left half
        self.blit(selected_text, (SCREEN_WIDTH / 4 - selected_text.get_width() / 2, title_1.get_height() - 20))
        
        # Draws upper right text + buttons
        title_2 = title_font.render("Wave {}/{}".format(self.curr_wave + 1, self.max_wave), 1, WHITE)
        left_btn = self.make_btn("<")
        right_btn = self.make_btn(">")
        
        title_2_x = SCREEN_WIDTH * 3 / 4 - title_2.get_width() / 2 # puts title_2 on the x center of the screen's right half
        left_right_y = (title_2.get_height() - left_btn.get_height()) / 2 # puts btns on the y center of title_2
        
        left_x = title_2_x - left_btn.get_width() - 20
        right_x = title_2_x + title_2.get_width() + 20
        
        self.blit(title_2, (title_2_x, 0))
        if self.curr_wave > 0:
            self.blit(left_btn, (left_x, left_right_y))
        if self.curr_wave < self.max_wave - 1:
            self.blit(right_btn, (right_x, left_right_y))
        
        self.left_btn_rect = left_btn.get_rect(x = left_x, y = left_right_y)
        self.right_btn_rect = right_btn.get_rect(x = right_x, y = left_right_y)
        
        # Draws towers
        for row, grid_row in enumerate(self.towers):
            for col, tower in enumerate(grid_row):
                
                tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"].convert_alpha(), self.get_dims())

                if not self.tower_selected[row][col]:
                    if self.num_selected == SAVE_DATA["game_attrs"]["max_towers"]["value"]:
                        tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                    else:
                        tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)

                self.blit(tower_img, self.get_locs(row, col))
                
        # Draws waves info
        wave_coords = (SCREEN_WIDTH / 2, GRID_MARGIN_Y - selected_text.get_height())
        self.draw_wave_info(wave_coords)
        self.blit(self.wave_info, wave_coords)
        
        # Draws map
        self.blit(self.map_img, (SCREEN_WIDTH * 3 / 4 - self.map_img.get_width() / 2, SCREEN_HEIGHT / 2 - 80))
                
        # Draws stuff at the bottom

        if self.difficulty == 0:
            difficulty = "Mild"
        elif self.difficulty == 1:
            difficulty = "Acute"
        else:
            difficulty = "Severe"
        difficulty_text = text_font.render("Difficulty: {}".format(difficulty), 1, WHITE)
        self.blit(difficulty_text, ((SCREEN_WIDTH - difficulty_text.get_width()) / 2, BTN_Y))

        """if self.difficulty > 0:
            minus_btn = self.make_btn("<")
            minus_x = SCREEN_WIDTH / 2 - difficulty_text.get_width() / 2 - minus_btn.get_width() - 20
            self.blit(minus_btn, (minus_x, BTN_Y))
            self.minus_btn_rect = minus_btn.get_rect(x=minus_x, y=BTN_Y)

        if self.difficulty < self.max_difficulty:
            plus_btn = self.make_btn(">")
            plus_x = SCREEN_WIDTH / 2 + difficulty_text.get_width() / 2 + 20
            self.blit(plus_btn, (plus_x, BTN_Y))
            self.plus_btn_rect = plus_btn.get_rect(x=plus_x, y=BTN_Y)"""

        start_btn = self.start_btn
        if self.num_selected == 0:
            start_btn = self.start_btn_disabled

        self.blit(start_btn, (self.start_btn_rect.x, BTN_Y))
        self.blit(self.back_btn, (BTN_X_MARGIN, BTN_Y))
        
        # Draws tower infos
        if self.over_tower[0] != -1:
            row, col = self.over_tower
            ind = row * GRID_ROW_SIZE + col
            
            if self.tower_infos[ind] == None:
                new_tower_info = TowerInfo(self.towers[row][col])
                self.tower_infos[ind] = new_tower_info.draw()
                
            self.blit(self.tower_infos[ind], self.tower_rects[row][col].topright)
                
        # Draws enemy infos
        if self.over_enemy != None:
            if self.enemy_infos.get(self.over_enemy) == None:
                if self.over_enemy in SAVE_DATA["seen_enemies"]:
                    enemy_name = clean_title(self.over_enemy)
                    new_enemy_info = HoverInfo(enemy_name, ENEMY_DATA[self.over_enemy]["description"])
                    self.enemy_infos[self.over_enemy] = new_enemy_info.draw()
                else:
                    new_enemy_info = HoverInfo("Unknown Enemy", "???")
                    self.enemy_infos[self.over_enemy] = new_enemy_info.draw()
            
            self.blit(self.enemy_infos[self.over_enemy],
                      self.enemy_infos[self.over_enemy].get_rect(topright = self.wave_data[self.over_enemy]["rect"].topleft))
                
        return self

    def get_difficulty(self):
        return self.difficulty

    def draw_map(self, map):
        img = map.make_map()

        # scales map down so that it is no bigger than a rectangle with dimensions (SCREEN_WIDTH / 2, SCREEN_WIDTH / 4)
        scale_factor = min((SCREEN_WIDTH / 2 - GRID_MARGIN_X) / img.get_width(), (SCREEN_HEIGHT / 2 - 40) / img.get_height())
        self.map_img = pg.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
    
    def draw_wave_info(self, wave_coords):
        wave_font = pg.font.Font(FONT, 50)
        enemy_surfs = []
        self.wave_data = {}
        
        for sub_wave in self.level_data["waves"][self.difficulty][self.curr_wave]:
            if self.wave_data.get(sub_wave["enemy_type"]):
                self.wave_data[sub_wave["enemy_type"]]["count"] += sub_wave["enemy_count"]
            else:
                self.wave_data[sub_wave["enemy_type"]] = {"count": sub_wave["enemy_count"]}
        
        wave_data_keys = list(self.wave_data)
        
        for enemy_type in wave_data_keys:
            text = wave_font.render("{}x".format(self.wave_data[enemy_type]["count"]), 1, WHITE)
            enemy_img = pg.transform.scale(ENEMY_DATA[enemy_type]["image"], (GRID_2_CELL_SIZE, GRID_2_CELL_SIZE)).convert_alpha()
            if enemy_type not in SAVE_DATA["seen_enemies"]:
                enemy_img.fill(DARK_GREY, special_flags=pg.BLEND_RGBA_MULT)
                font = pg.font.Font(FONT, MENU_TEXT_SIZE)
                question_mark = font.render("?", 1, WHITE)
                enemy_img.blit(question_mark, question_mark.get_rect(center = enemy_img.get_rect().center))
            enemy_surf = pg.Surface((text.get_width() + enemy_img.get_width(), max(text.get_height(), enemy_img.get_height())))
            
            enemy_surf.blit(text, (0, 0))
            enemy_surf.blit(enemy_img, (text.get_width(), 0))
            
            self.wave_data[enemy_type]["rect"] = pg.Rect(text.get_width(), 0, GRID_2_CELL_SIZE, GRID_2_CELL_SIZE)
            
            enemy_surfs.append(enemy_surf)
        
        self.wave_info = pg.Surface((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        x = 0
        y = 0
        for i, surf in enumerate(enemy_surfs):
            if x + surf.get_width() >= SCREEN_WIDTH / 2 - GRID_2_MARGIN_X:
                x = 0
                y += GRID_2_CELL_SIZE + GRID_SEPARATION
                
            self.wave_info.blit(surf, (x, y))
            
            self.wave_data[wave_data_keys[i]]["rect"].x += x + wave_coords[0]
            self.wave_data[wave_data_keys[i]]["rect"].y += y + wave_coords[1]
            
            x += surf.get_width() + GRID_2_SEPARATION
    
    def get_selected_towers(self):
        selected_towers = []
        for row, grid_row in enumerate(self.towers):
            for col, tower in enumerate(grid_row):
                if self.tower_selected[row][col]:
                    selected_towers.append(tower)
        return selected_towers
    
    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                
                if self.back_btn_rect.collidepoint(mouse_pos):
                    BTN_SFX.play()
                    return "menu"
                elif self.start_btn_rect.collidepoint(mouse_pos):
                    if self.num_selected > 0:
                        BTN_SFX.play()
                        return "game"
                    else:
                        WRONG_SELECTION_SFX.play()
                        
                elif self.left_btn_rect.collidepoint(mouse_pos) and self.curr_wave > 0:
                    BTN_2_SFX.play()
                    self.curr_wave -= 1
                elif self.right_btn_rect.collidepoint(mouse_pos) and self.curr_wave < self.max_wave - 1:
                    BTN_2_SFX.play()
                    self.curr_wave += 1
                    
                #elif self.difficulty > 0 and self.minus_btn_rect.collidepoint(mouse_pos):
                #    BTN_2_SFX.play()
                #    self.difficulty -= 1
                #    self.load_level_data()
                #elif self.difficulty < self.max_difficulty and self.plus_btn_rect.collidepoint(mouse_pos):
                #    BTN_2_SFX.play()
                #    self.difficulty += 1
                #    self.load_level_data()
                    
                elif self.over_tower[0] != -1:
                    row, col = self.over_tower
                    if self.tower_selected[row][col]:
                        BTN_2_SFX.play()
                        self.num_selected -= 1
                        self.tower_selected[row][col] = False
                    elif self.num_selected < SAVE_DATA["game_attrs"]["max_towers"]["value"]:
                        BTN_2_SFX.play()
                        self.num_selected += 1
                        self.tower_selected[row][col] = True
                    else:
                        WRONG_SELECTION_SFX.play()
                            
        if event.type == pg.MOUSEMOTION:
            mouse_pos = event.pos
            for row, grid_row in enumerate(self.tower_rects):
                for col, rect in enumerate(grid_row):
                    if rect.collidepoint(mouse_pos):
                        self.over_tower = [row, col]
                        return -1
                    
            for enemy_type in self.wave_data:
                if self.wave_data[enemy_type]["rect"].collidepoint(mouse_pos):
                    self.over_enemy = enemy_type
                    return -1
                    
            self.over_tower = [-1, -1]
            self.over_enemy = None
                        
        return -1

class HoverInfo(pg.Surface):
    def __init__(self, title, description):
        self.info_font = pg.font.Font(FONT, MENU_TEXT_SIZE)
        
        self.title = title
        self.description = description
        
        self.texts = []
        self.height = MENU_OFFSET
        self.width = MENU_OFFSET
        
    def make_title(self):
        title_font = pg.font.Font(FONT, MENU_TEXT_SIZE * 2)
        title_text = title_font.render(self.title, 1, WHITE)
        self.add_text(title_text)
    
    def make_description(self):
        text = textwrap.fill(self.description, 30 - round(MENU_TEXT_SIZE / 30)) # No idea how to really calculate this.
        text = text.split("\n")
        
        for i, part in enumerate(text):
            rendered_text = self.info_font.render(part, 1, WHITE)
            if i == len(text) - 1:
                self.add_text(rendered_text)
            else:
                self.add_text_custom(rendered_text, MENU_OFFSET // 5)
            
    def make_other_info(self):
        pass # to be overrided
    
    def add_text(self, text):
        self.add_text_custom(text, MENU_OFFSET)
        
    def add_text_custom(self, text, line_spacing): # only used when the line spacing is changed
        self.texts.append([text, line_spacing])
        self.height += text.get_height() + line_spacing
        self.width = max(self.width, text.get_width() + MENU_OFFSET * 2)
            
    def draw(self):
        self.make_title()
        self.make_description()
        self.make_other_info()
        
        super().__init__((self.width, self.height))
        self.fill(DARK_GREY)
        
        temp_height = MENU_OFFSET
        for text in self.texts:
            self.blit(text[0], (MENU_OFFSET, temp_height))
            temp_height += text[0].get_height() + text[1] # text[1] = line_spacing of the text
            
        return self
    
class LevelInfo(HoverInfo):
    def __init__(self, level, difficulty):
        self.unlocked = level <= SAVE_DATA["latest_level_unlocked"][difficulty]
        self.difficulty = difficulty
        self.level = level
        if self.unlocked:
            self.level_data = LEVEL_DATA[level]
            super().__init__(list(BODY_PARTS)[self.level_data["body_part"]].replace('_', ' ').title(),
                             self.level_data["description"][self.difficulty])
        else:
            super().__init__("???", "An unknown level. Complete the previous levels to unlock this one!")
        
    def make_other_info(self):
        if self.unlocked:
            ratings = ["Easy", "Medium", "Hard", "Very Hard", "Extreme"]
            colors = [GREEN, YELLOW, ORANGE, RED, MAROON]
            
            ratings_text = self.info_font.render(ratings[self.level_data["ratings"][self.difficulty]],
                                                 1, colors[self.level_data["ratings"][self.difficulty]])
            self.add_text(ratings_text)

            waves_text = self.info_font.render("{} Waves".format(len(self.level_data["waves"][self.difficulty])), 1, WHITE)
            self.add_text(waves_text)
            
            enemy_surf = pg.Surface((
                (MAX_ENEMIES_IN_ROW + 1) * (MENU_TEXT_SIZE + MENU_OFFSET),
                (len(self.level_data["enemies"][self.difficulty]) // MAX_ENEMIES_IN_ROW + 1) * (MENU_TEXT_SIZE + MENU_OFFSET)
            ))
            enemy_surf.fill(DARK_GREY)
            for i, enemy in enumerate(self.level_data["enemies"][self.difficulty]):
                enemy_image = pg.transform.scale(ENEMY_DATA[enemy]["image"], (MENU_TEXT_SIZE, MENU_TEXT_SIZE)).convert_alpha()
                if enemy not in SAVE_DATA["seen_enemies"]:
                    enemy_image.fill(DARK_GREY, special_flags=pg.BLEND_RGBA_MULT)
                    font = pg.font.Font(FONT, MENU_TEXT_SIZE)
                    question_mark = font.render("?", 1, WHITE)
                    enemy_image.blit(question_mark, question_mark.get_rect(center=enemy_image.get_rect().center))
                enemy_surf.blit(enemy_image, (i % MAX_ENEMIES_IN_ROW * (MENU_TEXT_SIZE + MENU_OFFSET),
                                              i // MAX_ENEMIES_IN_ROW * (MENU_TEXT_SIZE + MENU_OFFSET)))

            self.add_text(enemy_surf)
            
            high_score_text = self.info_font.render("Highest Protein Count: {}".format(SAVE_DATA["highscores"][self.level][self.difficulty]), 1, WHITE)
            self.add_text(high_score_text)
            
            protein_goal_text = self.info_font.render("Protein Count Goal: {}".format(LEVEL_DATA[self.level]["protein_goal"][self.difficulty]), 1, WHITE)
            self.add_text(protein_goal_text)
        
class TowerInfo(HoverInfo):
    def __init__(self, tower):
        self.tower_data = TOWER_DATA[tower]
        self.stages_data = self.tower_data["stages"]
        
        tower_name = clean_title(tower)
        super().__init__(tower_name, self.tower_data["description"])
        
    def make_other_info(self):
        stages_text = self.info_font.render("Stages: {}".format(len(self.stages_data)), 1, WHITE)
        self.add_text(stages_text)
        
        costs = []
        for i in range(len(self.stages_data)):
            costs.append(str(self.stages_data[i]["upgrade_cost"]))
        
        cost_text = self.info_font.render("Cost: {}".format("/".join(costs)), 1, WHITE)
        self.add_text(cost_text)

class UpgradesMenu(TowerMenu):
    def __init__(self):
        super().__init__()
        self.done_btn = self.make_btn("Done")
        self.done_btn_rect = pg.Rect(BTN_X_MARGIN, BTN_Y, self.done_btn.get_width(), self.done_btn.get_height())
        self.confirm_tower_menu = ActionMenu("Are you sure you want to buy this tower?", "Yes", "No")
        self.confirm_upgrade_menu = ActionMenu("Are you sure you want to buy this upgrade?", "Yes", "No")
        self.confirming = False

    def new(self, args):
        self.towers = []
        self.tower_rects = []
        self.tower_owned = []
        self.over_tower = [-1, -1]

        tower_names = list(TOWER_DATA)
        row = -1
        for i in range(len(TOWER_DATA)):
            if i % GRID_ROW_SIZE == 0:
                row += 1
                self.towers.append([])
                self.tower_rects.append([])
                self.tower_owned.append([])

            self.towers[row].append(tower_names[i])
            self.tower_rects[row].append(pg.Rect(self.get_locs(row, i % GRID_ROW_SIZE), self.get_dims()))
            self.tower_owned[row].append(tower_names[i] in SAVE_DATA["owned_towers"])

        self.tower_infos = [None for i in range(len(tower_names))]

        self.upgrade_names = list(SAVE_DATA["game_attrs"])
        self.upgrades = []
        self.upgrade_rects = []
        self.upgrade_button_rects = []
        self.is_maxed = []
        self.over_upgrade = -1
        height = GRID_MARGIN_Y
        for attr in SAVE_DATA["game_attrs"]:
            surf, rect, maxed = self.make_upgrade(attr, SAVE_DATA["game_attrs"][attr]["value"])
            self.upgrades.append(surf)
            self.upgrade_rects.append(surf.get_rect(topright=(SCREEN_WIDTH - GRID_MARGIN_X, height)))
            self.is_maxed.append(maxed)
            rect.topright = self.upgrade_rects[-1].topright
            self.upgrade_button_rects.append(rect)
            height += self.upgrade_button_rects[-1].height + MENU_OFFSET

        self.upgrade_infos = [None for i in range(len(self.upgrade_names))]

        font = pg.font.Font(FONT, 70)
        self.dna_text = font.render("DNA: " + str(SAVE_DATA["max_dna"] - SAVE_DATA["used_dna"]), 1, WHITE)

    def draw(self):
        self.fill(BLACK)

        title_font = pg.font.Font(FONT, 120)
        text_font = pg.font.Font(FONT, 70)

        title_1 = title_font.render("Buy Towers", 1, WHITE)
        self.blit(title_1, (SCREEN_WIDTH / 4 - title_1.get_width() / 2, 0)) # puts these on the x center of the screnn's left half

        for row, grid_row in enumerate(self.towers):
            for col, tower in enumerate(grid_row):
                tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"].convert_alpha(), self.get_dims())

                if not self.tower_owned[row][col]:
                    if self.is_tower_buyable(self.towers[row][col]):
                        tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)
                    else:
                        tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)

                self.blit(tower_img, self.get_locs(row, col))

        title_2 = title_font.render("Upgrades", 1, WHITE)
        self.blit(title_2, (SCREEN_WIDTH * 3 / 4 - title_1.get_width() / 2, 0))

        for i, attr in enumerate(self.upgrades):
            self.blit(attr, self.upgrade_rects[i])
            
        self.blit(self.done_btn, self.done_btn_rect)
        self.blit(self.dna_text, self.dna_text.get_rect(topright=(SCREEN_WIDTH - BTN_X_MARGIN, BTN_Y)))

        if not self.confirming:
            if self.over_tower[0] != -1:
                row, col = self.over_tower
                ind = row * GRID_ROW_SIZE + col

                if self.tower_infos[ind] == None:
                    new_tower_info = BuyTowerInfo(self.towers[row][col], -1 if self.tower_owned[row][col] else 1 if self.is_tower_buyable(self.towers[row][col]) else 0)
                    self.tower_infos[ind] = new_tower_info.draw()

                self.blit(self.tower_infos[ind], self.tower_rects[row][col].topright)
            elif self.over_upgrade != -1:
                if self.upgrade_infos[self.over_upgrade] == None:
                    new_upgrade_info = UpgradeInfo(self.upgrade_names[self.over_upgrade], 1 if self.is_upgrade_buyable(self.over_upgrade) else 0, self.is_maxed[self.over_upgrade])
                    self.upgrade_infos[self.over_upgrade] = new_upgrade_info.draw()
                self.blit(self.upgrade_infos[self.over_upgrade], self.upgrade_infos[self.over_upgrade].get_rect(top=self.upgrade_button_rects[self.over_upgrade].topleft[1], right = self.upgrade_button_rects[self.over_upgrade].topleft[0] - MENU_OFFSET))

        if self.confirming:
            self.blit(self.confirm_menu_surf, self.confirm_menu_rect)

        return self

    def make_upgrade(self, string, value):
        font = pg.font.Font(FONT, 70)
        text = font.render(clean_title(string) + ": " + str(value), 1, WHITE)
        plus_text = font.render("+", 1, WHITE)
        
        btn = pg.transform.scale(LEVEL_BUTTON_IMG, (plus_text.get_height(), plus_text.get_height())).copy().convert_alpha()
        btn.blit(plus_text, plus_text.get_rect(center=btn.get_rect().center))
        
        maxed = value == SAVE_DATA["game_attrs"][string]["max_value"]
        if maxed or not self.is_upgrade_buyable(string):
            btn.fill(LIGHT_GREY, None, pg.BLEND_RGB_MULT)
        
        btn_rect = btn.get_rect(topleft=(text.get_width() + MENU_OFFSET, 0))
        
        surf = pg.Surface((text.get_width() + MENU_OFFSET + btn.get_width(), btn_rect.height))
        surf.blit(text, (0, 0))
        surf.blit(btn, btn_rect)
        return surf, btn_rect, maxed

    def is_tower_buyable(self, tower):
        return SAVE_DATA["max_dna"] - SAVE_DATA["used_dna"] >= TOWER_DATA[tower]["unlock_cost"]

    def is_upgrade_buyable(self, upgrade): # Argument can be the upgrade's name or its index
        if isinstance(upgrade, int):
            upgrade = self.upgrade_names[upgrade]
        return SAVE_DATA["max_dna"] - SAVE_DATA["used_dna"] >= SAVE_DATA["game_attrs"][upgrade]["upgrade_cost"]

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.confirming:
                    if self.confirm_menu_rect.collidepoint(mouse_pos):
                        result = self.confirm_menu.event((mouse_pos[0] - self.confirm_menu_rect.x, mouse_pos[1] - self.confirm_menu_rect.y))
                        if result == 1:
                            BUY_SFX.play()
                            
                            if self.over_tower[0] != -1:
                                row, col = self.over_tower
                                SAVE_DATA["owned_towers"].append(self.towers[row][col])
                                SAVE_DATA["used_dna"] += TOWER_DATA[self.towers[row][col]]["unlock_cost"]
                                self.tower_owned[row][col] = True
                            else:
                                upgrade_name = self.upgrade_names[self.over_upgrade]
                                SAVE_DATA["game_attrs"][upgrade_name]["value"] += SAVE_DATA["game_attrs"][upgrade_name]["increment"]
                                SAVE_DATA["used_dna"] += SAVE_DATA["game_attrs"][upgrade_name]["upgrade_cost"]
                                SAVE_DATA["game_attrs"][upgrade_name]["upgrade_cost"] += SAVE_DATA["game_attrs"][upgrade_name]["cost_increment"]
                            
                            # Reload upgrades and upgrade btns whenever a tower/upgrade is bought
                            for i in range(len(self.upgrade_names)):
                                surf, rect, maxed = self.make_upgrade(self.upgrade_names[i], SAVE_DATA["game_attrs"][self.upgrade_names[i]]["value"])
                                self.upgrades[i] = surf
                                self.upgrade_rects[i] = surf.get_rect(topright=(SCREEN_WIDTH - GRID_MARGIN_X, self.upgrade_rects[i].top))
                                self.is_maxed[i] = maxed
                                rect.topright = self.upgrade_rects[i].topright
                                self.upgrade_button_rects[i] = rect
                                self.upgrade_infos[i] = None
                            self.tower_infos = [None for i in range(len(TOWER_DATA))] # Force a reload of all tower infos when buying a new tower
                                
                            font = pg.font.Font(FONT, 70)
                            self.dna_text = font.render("DNA: " + str(SAVE_DATA["max_dna"] - SAVE_DATA["used_dna"]), 1,
                                                        WHITE)
                        elif result == -1:
                            return -1
                        
                        else:
                            BTN_2_SFX.play()
                            
                    self.confirming = False
                    self.over_tower = [-1, -1]

                else:
                    if self.done_btn_rect.collidepoint(mouse_pos):
                        BTN_SFX.play()
                        return "menu"
                    elif self.over_tower[0] != -1:
                        row, col = self.over_tower
                        if not self.tower_owned[row][col]:
                            if self.is_tower_buyable(self.towers[row][col]):
                                BTN_2_SFX.play()
                                self.confirm_menu = self.confirm_tower_menu
                                self.confirm_menu_surf = self.confirm_menu.draw()
                                self.confirm_menu_rect = self.confirm_menu_surf.get_rect(
                                    center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                                self.confirming = True
                            elif not self.is_tower_buyable(self.towers[row][col]):
                                WRONG_SELECTION_SFX.play()
                    else:
                        if self.over_upgrade != -1:
                            if self.is_upgrade_buyable(self.over_upgrade) and not self.is_maxed[self.over_upgrade]:
                                BTN_2_SFX.play()
                                self.confirm_menu = self.confirm_upgrade_menu
                                self.confirm_menu_surf = self.confirm_menu.draw()
                                self.confirm_menu_rect = self.confirm_menu_surf.get_rect(
                                    center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                                self.over_upgrade = self.over_upgrade
                                self.confirming = True
                            else:
                                WRONG_SELECTION_SFX.play()

        if event.type == pg.MOUSEMOTION and not self.confirming:
            mouse_pos = event.pos
            for row, grid_row in enumerate(self.tower_rects):
                for col, rect in enumerate(grid_row):
                    if rect.collidepoint(mouse_pos):
                        self.over_tower = [row, col]
                        self.over_upgrade = -1
                        return -1

            self.over_tower = [-1, -1]
            for i, rect in enumerate(self.upgrade_button_rects):
                if rect.collidepoint(mouse_pos):
                    self.over_upgrade = i
                    return -1

            self.over_upgrade = -1

        return -1

class BuyTowerInfo(TowerInfo):
    def __init__(self, tower, buyable):
        self.buyable = buyable
        super().__init__(tower)

    def make_other_info(self):
        if self.buyable == 0:
            unlock_text = self.info_font.render("Unlock Cost: " + str(self.tower_data["unlock_cost"]), 1, RED)
            self.add_text(unlock_text)
            error_text = self.info_font.render("Insufficient DNA to buy this tower!", 1, RED)
            self.add_text(error_text)
        elif self.buyable == 1:
            unlock_text = self.info_font.render("Unlock Cost: " + str(self.tower_data["unlock_cost"]), 1, YELLOW)
            self.add_text(unlock_text)
        else:
            unlock_text = self.info_font.render("You own this tower!", 1, GREEN)
            self.add_text(unlock_text)

        super().make_other_info()

class UpgradeInfo(HoverInfo):
    def __init__(self, upgrade, buyable, maxed):
        self.buyable = buyable
        self.maxed = maxed
        self.upgrade_data = SAVE_DATA["game_attrs"][upgrade]
        upgrade_name = (" ".join(upgrade.split("_"))).title()  # removes underscores, capitalizes it properly
        super().__init__(upgrade_name, self.upgrade_data["description"])

    def make_other_info(self):
        if not self.maxed:
            if self.buyable == 0:
                unlock_text = self.info_font.render("Upgrade Cost: " + str(self.upgrade_data["upgrade_cost"]), 1, RED)
                self.add_text(unlock_text)
                error_text = self.info_font.render("Insufficient DNA to buy this upgrade!", 1, RED)
                self.add_text(error_text)
            else:
                unlock_text = self.info_font.render("Upgrade Cost: " + str(self.upgrade_data["upgrade_cost"]), 1, YELLOW)
                self.add_text(unlock_text)

        new_value_text = self.info_font.render("Current Value: " + str(self.upgrade_data["value"]), 1, WHITE)
        self.add_text(new_value_text)
        
        if not self.maxed:
            if self.buyable == 1:
                new_value_text = self.info_font.render("Upgraded Value: " + str(self.upgrade_data["value"] + self.upgrade_data["increment"]), 1, GREEN)
                self.add_text(new_value_text)
        else:
            maxed_text = self.info_font.render("This upgrade has been maxed out!", 1, GREEN)
            self.add_text(maxed_text)

        super().make_other_info()

# In the future we can use this for other menus that only take up half the screen e.g. in tutorials, and such.

class ActionMenu(pg.Surface):
    def __init__(self, message, btn1txt, btn2txt):
        large_font = pg.font.Font(FONT, 70)
        self.texts = []
        self.height = MENU_OFFSET * 2
        self.width = SCREEN_WIDTH / 2
        text = textwrap.fill(message, 30)  # Hardcoding lmao

        for part in text.split('\n'):
            rendered_text = large_font.render(part, 1, WHITE)
            self.texts.append(rendered_text)
            self.height += rendered_text.get_height() + round(MENU_OFFSET / 2)
            self.width = max(self.width, rendered_text.get_width() + MENU_OFFSET * 4)

        self.button1 = self.make_btn(btn1txt)
        self.button2 = self.make_btn(btn2txt)
        self.height += self.button1.get_height() + round(MENU_OFFSET / 2)
        self.button1_rect = self.button1.get_rect(bottomleft=(MENU_OFFSET, self.height - MENU_OFFSET))
        self.button2_rect = self.button2.get_rect(bottomright=(self.width - MENU_OFFSET, self.height - MENU_OFFSET))

    def draw(self):
        super().__init__((self.width, self.height))

        self.fill(DARK_GREY)
        t_height = MENU_OFFSET
        for text in self.texts:
            self.blit(text, text.get_rect(centerx=self.width / 2, y=t_height))
            t_height += text.get_height() + round(MENU_OFFSET / 2)

        self.blit(self.button1, self.button1_rect)
        self.blit(self.button2, self.button2_rect)

        return self

    def make_btn(self, string):
        font = pg.font.Font(FONT, 70)
        text = font.render(string, 1, WHITE)
        btn = pg.transform.scale(LEVEL_BUTTON_IMG,
                                 (text.get_width() + BTN_PADDING * 2, text.get_height())).copy().convert_alpha()
        btn.blit(text, text.get_rect(center=btn.get_rect().center))
        return btn

    def event(self, mouse_pos):
        if self.button1_rect.collidepoint(mouse_pos):
            return 1
        elif self.button2_rect.collidepoint(mouse_pos):
            return 2
        else:
            return -1
