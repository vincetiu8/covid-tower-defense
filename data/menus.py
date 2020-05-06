import textwrap

from data.display import *
from data.tilemap import Camera
from data.settings import *
from data.dev_tools import TowerPreview, EnemyPreview

class StartMenu(Display):
    def __init__(self):
        super().__init__()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)
        
    def draw(self):
        self.fill(BLACK)
        self.blit(self.camera.apply_image(START_SCREEN_IMG), self.camera.apply_rect(pg.Rect(0, 0, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)))
        
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
        self.level_buttons = [pg.Rect((20, 400), self.level_button_rect.size), pg.Rect((160, 400), self.level_button_rect.size), pg.Rect((300, 400), self.level_button_rect.size)]
        
        self.tower_preview_button = pg.Rect((1200, 100), self.level_button_rect.size)
        self.enemy_preview_button = pg.Rect((1200, 500), self.level_button_rect.size)
        self.level_preview_button = pg.Rect((1200, 900), self.level_button_rect.size)
        
        self.base_zoom = self.camera.get_zoom()
        self.zoom_step = -1
        self.body_images = []
        self.body_image = self.camera.apply_image(BODY_IMG)
        
        self.init_body_1()
        
        self.level_infos = [None for i in range(len(LEVEL_DATA))]
        self.over_level = -1
        
    def init_body_1(self): #inits half the body_images on game startup
        for i in range(5):
            self.camera.zoom(ZOOM_AMT_MENU)
            self.body_images.append(self.camera.apply_image(BODY_IMG))
        
    def new(self, args): #inits the other half
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

        for i, button in enumerate(self.level_buttons):
            self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(button))
            lives_text = lives_font.render(str(i + 1), 1, WHITE)
            self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple((button.center[0] - lives_text.get_rect().center[0], button.center[1] - lives_text.get_rect().center[1])))

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.tower_preview_button))
        lives_text = lives_font.render("Tower", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0], self.tower_preview_button.center[1] - lives_text.get_rect().center[1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Preview", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.tower_preview_button.center[0] - lives_text.get_rect().center[0], self.tower_preview_button.center[1] - lives_text.get_rect().center[1] + lives_text.get_rect().height - MENU_OFFSET)))

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

        self.blit(self.camera.apply_image(LEVEL_BUTTON_IMG), self.camera.apply_rect(self.level_preview_button))
        lives_text = lives_font.render("Level", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.level_preview_button.center[0] - lives_text.get_rect().center[0],
             self.level_preview_button.center[1] - lives_text.get_rect().center[
                 1] - lives_text.get_rect().height + MENU_OFFSET)))
        lives_text = lives_font.render("Preview", 1, WHITE)
        self.blit(self.camera.apply_image(lives_text), self.camera.apply_tuple(
            (self.level_preview_button.center[0] - lives_text.get_rect().center[0],
             self.level_preview_button.center[1] - lives_text.get_rect().center[
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

    def get_level_info(self, level):
        height = MENU_OFFSET

        level_data = LEVEL_DATA[level]
        title_font = pg.font.Font(FONT, MENU_TEXT_SIZE * 2)
        texts = []
        title_text = title_font.render(level_data["title"], 1, WHITE)
        texts.append(title_text)
        height += title_text.get_height() + MENU_OFFSET

        description_font = pg.font.Font(FONT, MENU_TEXT_SIZE)
        text = textwrap.fill(level_data["description"], 30 - round(MENU_TEXT_SIZE / 30)) # No idea how to really calculate this.
        counter = 0
        for part in text.split('\n'):
            rendered_text = description_font.render(part, 1, WHITE)
            texts.append(rendered_text)
            height += rendered_text.get_height() + MENU_OFFSET
            counter += 1

        if level_data["difficulty"] == 0:
            difficulty_text = description_font.render("Easy", 1, GREEN)
        elif level_data["difficulty"] == 1:
            difficulty_text = description_font.render("Medium", 1, YELLOW)
        elif level_data["difficulty"] == 2:
            difficulty_text = description_font.render("Hard", 1, ORANGE)
        elif level_data["difficulty"] == 3:
            difficulty_text = description_font.render("Very Hard", 1, RED)
        elif level_data["difficulty"] == 4:
            difficulty_text = description_font.render("Extreme", 1, MAROON)
        texts.append(difficulty_text)
        height += difficulty_text.get_height() + MENU_OFFSET

        waves_text = description_font.render("{} Waves".format(len(level_data["waves"])), 1, WHITE)
        texts.append(waves_text)
        height += waves_text.get_height() + MENU_OFFSET

        enemy_surf = pg.Surface((title_text.get_size()[0] + MENU_OFFSET * 2, MENU_TEXT_SIZE))
        enemy_surf.fill(DARKGREY)
        for i, enemy in enumerate(level_data["enemies"]):
            enemy_image = pg.transform.scale(ENEMY_DATA[enemy]["image"], (MENU_TEXT_SIZE, MENU_TEXT_SIZE))
            enemy_surf.blit(enemy_image, (i * (MENU_TEXT_SIZE + MENU_OFFSET), 0))

        texts.append(enemy_surf)
        height += enemy_surf.get_height()

        level_surf = pg.Surface((title_text.get_width() + MENU_OFFSET * 2, height + MENU_OFFSET))
        level_surf.fill(DARKGREY)
        temp_height = MENU_OFFSET
        for text in texts:
            level_surf.blit(text, (MENU_OFFSET, temp_height))
            temp_height += text.get_height() + MENU_OFFSET

        self.level_descs[level] = level_surf

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
                elif self.level_preview_button.collidepoint(mouse_pos):
                    return "level_preview"
                
                if self.over_level != -1:
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
        self.start_btn_disabled.fill(LIGHTGREY, None, pg.BLEND_RGB_MULT)
        
        self.over_tower = [-1, -1]
        
    def new(self, args):
        self.towers = []
        self.tower_rects = []
        self.tower_selected = []
        self.num_selected = 0
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
        
    def draw(self):
        self.fill(BLACK)
        
        title_font = pg.font.Font(FONT, 160)
        text_font = pg.font.Font(FONT, 80)
        
        title = title_font.render("Select Towers", 1, WHITE)
        self.blit(title, ((SCREEN_WIDTH - title.get_width()) / 2, 0))
        
        selected_text = text_font.render("Selected: {}/{}".format(self.num_selected, NUM_ALLOWED), 1, WHITE)
        self.blit(selected_text, ((SCREEN_WIDTH - selected_text.get_width()) / 2, BTN_Y))
        
        for row, grid_row in enumerate(self.towers):
            for col, tower in enumerate(grid_row):
                
                tower_img = pg.transform.scale(TOWER_DATA[tower]["stages"][0]["image"].convert_alpha(), self.get_dims())

                if not self.tower_selected[row][col]:
                    if self.num_selected == NUM_ALLOWED:
                        tower_img.fill(HALF_RED, None, pg.BLEND_RGBA_MULT)
                    else:
                        tower_img.fill(HALF_WHITE, None, pg.BLEND_RGBA_MULT)

                self.blit(tower_img, self.get_locs(row, col))
                
        start_btn = self.start_btn
        if self.num_selected == 0:
            start_btn = self.start_btn_disabled

        self.blit(start_btn, (self.start_btn_rect.x, BTN_Y))
        self.blit(self.back_btn, (BTN_X_MARGIN, BTN_Y))
        
        if self.over_tower[0] != -1:
            row, col = self.over_tower
            ind = row * GRID_ROW_SIZE + col
            
            if self.tower_infos[ind] == None:
                new_tower_info = TowerInfo(self.towers[row][col])
                self.tower_infos[ind] = new_tower_info.draw()
                
            if self.tower_rects[row][col].centerx < self.get_width() / 2:
                self.blit(self.tower_infos[ind], self.tower_rects[row][col].topright)
            else:
                self.blit(self.tower_infos[ind], self.tower_infos[ind].get_rect(topright = self.tower_rects[row][col].topleft))
                
        return self
                
    def get_dims(self):
        return (GRID_CELL_SIZE, GRID_CELL_SIZE)
                
    def get_locs(self, row, col):
        x = GRID_MARGIN_X + col * (GRID_CELL_SIZE + GRID_SEPARATION)
        y = GRID_MARGIN_Y + row * (GRID_CELL_SIZE + GRID_SEPARATION)
        
        return (x, y)
    
    def make_btn(self, string):
        font = pg.font.Font(FONT, 100)
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
                    
            self.over_tower = [-1, -1]
                        
        return -1

class HoverInfo(pg.Surface):
    def __init__(self, title, description, menu_offset):
        self.menu_offset = menu_offset
        self.info_font = pg.font.Font(FONT, MENU_TEXT_SIZE)
        
        self.title = title
        self.description = description
        
        self.texts = []
        self.height = self.menu_offset
        self.width = self.menu_offset
        
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
        self.height += text.get_height() + self.menu_offset
        self.width = max(self.width, text.get_width() + self.menu_offset * 2)
            
    def draw(self):
        self.make_title()
        self.make_description()
        self.make_other_info()
        
        super().__init__((self.width, self.height + self.menu_offset))
        self.fill(DARKGREY)
        
        temp_height = self.menu_offset
        for text in self.texts:
            self.blit(text, (self.menu_offset, temp_height))
            temp_height += text.get_height() + self.menu_offset
            
        return self
    
class LevelInfo(HoverInfo):
    def __init__(self, level):
        self.level_data = LEVEL_DATA[level]
        super().__init__(self.level_data["title"], self.level_data["description"], MENU_OFFSET)
        
    def make_other_info(self):
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

        enemy_surf = pg.Surface((self.texts[0].get_width() + self.menu_offset * 2, MENU_TEXT_SIZE))
        enemy_surf.fill(DARKGREY)
        for i, enemy in enumerate(self.level_data["enemies"]):
            enemy_image = pg.transform.scale(ENEMY_DATA[enemy]["image"], (MENU_TEXT_SIZE, MENU_TEXT_SIZE))
            enemy_surf.blit(enemy_image, (i * (MENU_TEXT_SIZE + self.menu_offset), 0))

        self.add_text(enemy_surf)
        
class TowerInfo(HoverInfo):
    def __init__(self, tower):
        self.tower_data = TOWER_DATA[tower]
        self.stages_data = self.tower_data["stages"]
        
        tower_name = (" ".join(tower.split("_"))).title() # removes underscores, capitalizes it properly
        super().__init__(tower_name, self.tower_data["description"], MENU_OFFSET_2)
        
    def make_other_info(self):
        text_names = ["Damage", "Fire Rate", "Range", "Cost", "Directions", "Tracks Enemies"]
        keys = ["damage", "bullet_spawn_speed", "range", "upgrade_cost", "directions", "tracking"]
        
        stages_text = self.info_font.render("Stages: {}".format(len(self.stages_data)), 1, WHITE)
        self.add_text(stages_text)
        
        for i in range(len(text_names)):
            self.make_text(text_names[i], keys[i])
        
    def make_text(self, text_name, key):
        texts = []
        map_tf = {True: "Yes", False: "No"}
        
        for i in range(len(self.stages_data)):
            to_add = self.stages_data[i][key]
            
            if isinstance(to_add, bool):
                texts.append(map_tf[to_add])
            else:
                texts.append(str(to_add))
            
        text = self.info_font.render("{}: {}".format(text_name, "/".join(texts)), 1, WHITE)
        self.add_text(text)
