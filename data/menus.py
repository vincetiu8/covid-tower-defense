import textwrap

from data.display import *
from data.tilemap import Camera, TiledMap
from data.settings import *
from data.dev_tools import TowerEditMenu, EnemyEditMenu

class StartMenu(Display):        
    def draw(self):
        self.fill(BLACK)
        self.blit(START_SCREEN_IMG, ((SCREEN_WIDTH - START_SCREEN_IMG.get_width()) / 2, 0))
        
        return self
    
    def event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                return "menu"
                
        return -1
    
class Menu(Display):
    def __init__(self):
        super().__init__()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.level_button_rect = LEVEL_BUTTON_IMG.get_rect()
        self.level_buttons = [pg.Rect((-80 + 140 * i, 400), self.level_button_rect.size) for i in range(len(LEVEL_DATA))]

        self.tower_preview_button = pg.Rect((800, 200), self.level_button_rect.size)
        self.enemy_preview_button = pg.Rect((800, 600), self.level_button_rect.size)
        self.tower_edit_button = pg.Rect((1200, 200), self.level_button_rect.size)
        self.enemy_edit_button = pg.Rect((1200, 600), self.level_button_rect.size)
        self.level_edit_button = pg.Rect((1200, 1000), self.level_button_rect.size)
        self.options_button = pg.Rect((850, -100), OPTIONS_IMGS[0].get_size())
        
        self.base_zoom = self.camera.get_zoom()
        self.zoom_step = -1
        self.body_images = []
        self.body_image = self.camera.apply_image(BODY_IMG)
        
        self.init_body_1()

        self.over_level = -1
        
    def init_body_1(self): #inits half the body_images on game startup
        for i in range(5):
            self.camera.zoom(ZOOM_AMT_MENU)
            self.body_images.append(self.camera.apply_image(BODY_IMG))
        
    def new(self, args): #inits the other half
        self.level_infos = [None for i in range(len(LEVEL_DATA))]
        if len(self.body_images) < 6: # so this will only run when first switching to menu
            while self.camera.zoom(ZOOM_AMT_MENU) != False:
                self.body_images.append(self.camera.apply_image(BODY_IMG))
            self.camera.zoom(self.base_zoom - self.camera.get_zoom())

    def update(self):
        self.update_level()

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
        self.fill((0, 0, 0))
        
        self.blit(self.body_image, self.camera.apply_tuple((-775, 150)))

        big_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w * 4)
        lives_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w)
        level_text = big_font.render("Levels", 1, WHITE)
        self.blit(self.camera.apply_image(level_text), self.camera.apply_tuple((START_SCREEN_IMG.get_rect().w / 2 - level_text.get_rect().center[0], -50 - level_text.get_rect().center[1])))
        
        hover_options = self.options_button.collidepoint(self.camera.correct_mouse(pg.mouse.get_pos()))
        self.blit(self.camera.apply_image(OPTIONS_IMGS[hover_options]), self.camera.apply_rect(self.options_button))

        for i, button in enumerate(self.level_buttons):
            if SAVE_DATA["level"] >= i:
                self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(button))
                lives_text = lives_font.render(str(i + 1), 1, WHITE)
                self.blit(self.camera.apply_image(lives_text), self.camera.apply_rect(lives_text.get_rect(center=button.center)))
            else:
                grey_image = LEVEL_BUTTON_IMG.copy()
                grey_image.fill(DARK_GREY, special_flags=pg.BLEND_RGB_MIN)
                self.blit(self.camera.apply_image(grey_image), self.camera.apply_rect(button))
                self.blit(self.camera.apply_image(LOCK_IMG), self.camera.apply_rect(LOCK_IMG.get_rect(center=button.center)))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.tower_preview_button))
        lives_text = lives_font.render("Tower", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0],
             self.tower_preview_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Preview", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0],
             self.tower_preview_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET)))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.enemy_preview_button))
        lives_text = lives_font.render("Enemy", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.enemy_preview_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_preview_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Preview", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.enemy_preview_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_preview_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET)))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.tower_edit_button))
        lives_text = lives_font.render("Tower", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_edit_button.center[0] - lives_text.get_rect().center[0], self.tower_edit_button.center[1] - lives_text.get_rect().center[1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Edit", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_edit_button.center[0] - lives_text.get_rect().center[0], self.tower_edit_button.center[1] - lives_text.get_rect().center[1] + lives_text.get_rect().height - MENU_OFFSET)))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.enemy_edit_button))
        lives_text = lives_font.render("Enemy", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.enemy_edit_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_edit_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Edit", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.enemy_edit_button.center[0] - lives_text.get_rect().center[0],
             self.enemy_edit_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET)))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.level_edit_button))
        lives_text = lives_font.render("Level", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.level_edit_button.center[0] - lives_text.get_rect().center[0],
             self.level_edit_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Edit", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.level_edit_button.center[0] - lives_text.get_rect().center[0],
             self.level_edit_button.center[1] - lives_text.get_rect().center[
                 1] + lives_text.get_rect().height - MENU_OFFSET)))

        if self.over_level != -1:
            if self.level_infos[self.over_level] == None:
                new_level_info = LevelInfo(self.over_level)
                self.level_infos[self.over_level] = new_level_info.draw()

            if self.level_buttons[self.over_level].centerx < self.get_width() / 2:
                self.blit(self.camera.apply_image(self.level_infos[self.over_level]), self.camera.apply_tuple(self.level_buttons[self.over_level].topright))
            else:
                self.blit(self.camera.apply_image(self.level_infos[self.over_level]), self.camera.apply_rect(self.level_infos[self.over_level].get_rect(topright = self.level_buttons[self.over_level].topleft)))
                
        return self

    def update_level(self):
        mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
        for i, button in enumerate(self.level_buttons):
            if button.collidepoint(mouse_pos):
                self.over_level = i
                return
            
        self.over_level = -1

    def get_over_level(self):
        return self.over_level
    
    def update_body_img(self):
        if self.zoom_step >= 0:
            self.body_image = self.body_images[self.zoom_step]
        else:
            self.body_image = self.camera.apply_image(BODY_IMG)

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
                if self.tower_preview_button.collidepoint(mouse_pos):
                    return "tower_preview"
                elif self.enemy_preview_button.collidepoint(mouse_pos):
                    return "enemy_preview"
                elif self.tower_edit_button.collidepoint(mouse_pos):
                    return "tower_edit"
                elif self.enemy_edit_button.collidepoint(mouse_pos):
                    return "enemy_edit"
                elif self.level_edit_button.collidepoint(mouse_pos):
                    return "level_edit"
                elif self.options_button.collidepoint(mouse_pos):
                    return "options"
                
                if self.over_level != -1 and self.over_level <= SAVE_DATA["level"]:
                    return "tower_select"

            elif event.button == 4:
                if self.camera.zoom(ZOOM_AMT_MENU) != False:
                    self.zoom_step += 1
                    self.update_body_img()

            elif event.button == 5:
                if self.camera.zoom(-ZOOM_AMT_MENU) != False:
                    self.zoom_step -= 1
                    self.update_body_img()

        return -1
    
class TowerSelectMenu(Display):
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
        map = TiledMap(path.join(MAP_FOLDER, "map{}.tmx".format(args[0])))
        self.map_img = None
        self.draw_map(map)
        
        self.max_wave = len(self.level_data["waves"])
        
        self.towers = []
        self.tower_rects = []
        self.tower_selected = []
        
        self.over_tower = [-1, -1]
        self.curr_wave = 0
        self.num_selected = 0
        
        self.wave_info = None
        
        self.over_enemy = None
        self.wave_data = {}
        
        tower_names = list(TOWER_DATA)
        
        row = -1
        for i in range(len(TOWER_DATA)):
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
        
    def draw(self):
        self.fill(BLACK)
        
        title_font = pg.font.Font(FONT, 120)
        text_font = pg.font.Font(FONT, 70)
        
        # Draws upper left text
        title_1 = title_font.render("Select Towers", 1, WHITE)
        selected_text = text_font.render("Selected: {}/{}".format(self.num_selected, NUM_ALLOWED), 1, WHITE)
        
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
        self.blit(left_btn, (left_x, left_right_y))
        self.blit(right_btn, (right_x, left_right_y))
        
        self.left_btn_rect = left_btn.get_rect(x = left_x, y = left_right_y)
        self.right_btn_rect = right_btn.get_rect(x = right_x, y = left_right_y)
        
        # Draws towers
        for row, grid_row in enumerate(self.towers):
            for col, tower in enumerate(grid_row):
                
                tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"].convert_alpha(), self.get_dims())

                if not self.tower_selected[row][col]:
                    if self.num_selected == NUM_ALLOWED:
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
        level_text = text_font.render("Level: {}".format(self.level_data["title"]), 1, WHITE)
        self.blit(level_text, ((SCREEN_WIDTH - level_text.get_width()) / 2, BTN_Y))
                
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
                enemy_name = clean_title(self.over_enemy)
                new_enemy_info = HoverInfo(enemy_name, ENEMY_DATA[self.over_enemy]["description"])
                self.enemy_infos[self.over_enemy] = new_enemy_info.draw()
            
            self.blit(self.enemy_infos[self.over_enemy],
                      self.enemy_infos[self.over_enemy].get_rect(topright = self.wave_data[self.over_enemy ]["rect"].topleft))
                
        return self
    
    def draw_map(self, map):
        img = map.make_map()
        img.blit(map.make_objects(), (0, 0))
        
        # scales map down so that it is no bigger than a rectangle with dimensions (SCREEN_WIDTH / 2, SCREEN_WIDTH / 4)
        scale_factor = min((SCREEN_WIDTH / 2 - GRID_MARGIN_X) / img.get_width(), (SCREEN_HEIGHT / 2 - 40) / img.get_height())
        self.map_img = pg.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
    
    def draw_wave_info(self, wave_coords):
        wave_font = pg.font.Font(FONT, 50)
        enemy_surfs = []
        self.wave_data = {}
        
        for sub_wave in self.level_data["waves"][self.curr_wave]:
            if self.wave_data.get(sub_wave["enemy_type"]):
                self.wave_data[sub_wave["enemy_type"]]["count"] += sub_wave["enemy_count"]
            else:
                self.wave_data[sub_wave["enemy_type"]] = {"count": sub_wave["enemy_count"]}
        
        wave_data_keys = list(self.wave_data)
        
        for enemy_type in wave_data_keys:
            text = wave_font.render("{}x".format(self.wave_data[enemy_type]["count"]), 1, WHITE)
            enemy_img = pg.transform.scale(ENEMY_DATA[enemy_type]["image"], (GRID_2_CELL_SIZE, GRID_2_CELL_SIZE))
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
                
    def get_dims(self):
        return (GRID_CELL_SIZE, GRID_CELL_SIZE)
                
    def get_locs(self, row, col):
        x = GRID_MARGIN_X + col * (GRID_CELL_SIZE + GRID_SEPARATION)
        y = GRID_MARGIN_Y + row * (GRID_CELL_SIZE + GRID_SEPARATION)
        
        return (x, y)
    
    def make_btn(self, string):
        font = pg.font.Font(FONT, 70)
        text = font.render(string, 1, WHITE)
        btn = pg.transform.scale(LEVEL_BUTTON_IMG, (text.get_width() + BTN_PADDING * 2, text.get_height())).copy().convert_alpha()
        btn.blit(text, text.get_rect(center = btn.get_rect().center))
        return btn
    
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
                mouse_pos = pg.mouse.get_pos()
                
                if self.back_btn_rect.collidepoint(mouse_pos):
                    return "menu"
                elif self.start_btn_rect.collidepoint(mouse_pos) and self.num_selected > 0:
                    return "game"
                elif self.left_btn_rect.collidepoint(mouse_pos):
                    self.curr_wave = max(self.curr_wave - 1, 0)
                elif self.right_btn_rect.collidepoint(mouse_pos):
                    self.curr_wave = min(self.curr_wave + 1, self.max_wave - 1)
                elif self.over_tower[0] != -1:
                    row, col = self.over_tower
                    if self.tower_selected[row][col]:
                        self.num_selected -= 1
                        self.tower_selected[row][col] = False
                    elif self.num_selected < NUM_ALLOWED:
                        self.num_selected += 1
                        self.tower_selected[row][col] = True
                            
        if event.type == pg.MOUSEMOTION:
            mouse_pos = pg.mouse.get_pos()
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
        
        for part in text.split('\n'):
            rendered_text = self.info_font.render(part, 1, WHITE)
            self.add_text(rendered_text)
            
    def make_other_info(self):
        pass # to be overrided
    
    def add_text(self, text):
        self.texts.append(text)
        self.height += text.get_height() + MENU_OFFSET
        self.width = max(self.width, text.get_width() + MENU_OFFSET * 2)
            
    def draw(self):
        self.make_title()
        self.make_description()
        self.make_other_info()
        
        super().__init__((self.width, self.height + MENU_OFFSET))
        self.fill(DARK_GREY)
        
        temp_height = MENU_OFFSET
        for text in self.texts:
            self.blit(text, (MENU_OFFSET, temp_height))
            temp_height += text.get_height() + MENU_OFFSET
            
        return self
    
class LevelInfo(HoverInfo):
    def __init__(self, level):
        self.unlocked = level <= SAVE_DATA["level"]
        if self.unlocked:
            self.level_data = LEVEL_DATA[level]
            super().__init__(self.level_data["title"], self.level_data["description"])
        else:
            super().__init__("???", "An unknown level. Complete the previous levels to unlock this one!")
        
    def make_other_info(self):
        if self.unlocked:
            if self.level_data["difficulty"] == 0:
                difficulty_text = self.info_font.render("Easy", 1, GREEN)
            elif self.level_data["difficulty"] == 1:
                difficulty_text = self.info_font.render("Medium", 1, YELLOW)
            elif self.level_data["difficulty"] == 2:
                difficulty_text = self.info_font.render("Hard", 1, ORANGE)
            elif self.level_data["difficulty"] == 3:
                difficulty_text = self.info_font.render("Very Hard", 1, RED)
            elif self.level_data["difficulty"] == 4:
                difficulty_text = self.info_font.render("Extreme", 1, MAROON)
            self.add_text(difficulty_text)

            waves_text = self.info_font.render("{} Waves".format(len(self.level_data["waves"])), 1, WHITE)
            self.add_text(waves_text)

            enemy_surf = pg.Surface((self.texts[0].get_width() + MENU_OFFSET * 2, MENU_TEXT_SIZE))
            enemy_surf.fill(DARK_GREY)
            for i, enemy in enumerate(self.level_data["enemies"]):
                enemy_image = pg.transform.scale(ENEMY_DATA[enemy]["image"], (MENU_TEXT_SIZE, MENU_TEXT_SIZE))
                enemy_surf.blit(enemy_image, (i * (MENU_TEXT_SIZE + MENU_OFFSET), 0))

            self.add_text(enemy_surf)
        
class TowerInfo(HoverInfo):
    def __init__(self, tower):
        self.tower_data = TOWER_DATA[tower]
        self.stages_data = self.tower_data["stages"]
        
        tower_name = clean_title(tower)
        super().__init__(tower_name, self.tower_data["description"])
        
    def make_other_info(self):
        text_names = ["Damage", "Attack Speed", "Range", "Cost"]
        keys = ["damage", "attack_speed", "range", "upgrade_cost"]
        
        stages_text = self.info_font.render("Stages: {}".format(len(self.stages_data)), 1, WHITE)
        self.add_text(stages_text)
        
        costs = []
        for i in range(len(self.stages_data)):
            costs.append(str(self.stages_data[i]["upgrade_cost"]))
        
        cost_text = self.info_font.render("Cost: {}".format("/".join(costs)), 1, WHITE)
        self.add_text(cost_text)
