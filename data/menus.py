import textwrap

from data.display import *
from data.tilemap import Camera
from data.settings import *
from data.dev_tools import TowerPreview

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
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, START_SCREEN_IMG.get_rect().w, START_SCREEN_IMG.get_rect().h)
        self.level_button_rect = LEVEL_BUTTON_IMG.get_rect()
        self.level_buttons = [pg.Rect((20, 120), self.level_button_rect.size), pg.Rect((160, 120), self.level_button_rect.size), pg.Rect((300, 120), self.level_button_rect.size)]
        self.tower_preview_button = pg.Rect((600, 100), self.level_button_rect.size)
        self.level_descs = [None for i in range(len(LEVEL_DATA))]
        self.over_level = -1
        self.tower_preview = None

    def update(self):
        self.update_level()
        if self.tower_preview != None:
            self.tower_preview.update()

    def draw(self):
        self.fill((0, 0, 0))

        lives_font = pg.font.Font(FONT, LEVEL_BUTTON_IMG.get_rect().w)
        level_text = lives_font.render("Levels", 1, WHITE)
        self.blit(self.camera.apply_image(level_text), self.camera.apply_tuple((START_SCREEN_IMG.get_rect().w / 2 - level_text.get_rect().center[0], 75 - level_text.get_rect().center[1])))

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

        if self.tower_preview != None:
            temp_surf = self.tower_preview.draw()
            self.blit(temp_surf, (MENU_OFFSET, MENU_OFFSET))
            return self

        if self.over_level != -1:
            if self.level_descs[self.over_level] == None:
                self.get_level_info(self.over_level)
            if self.level_buttons[self.over_level].centerx < self.get_width() / 2:
                self.blit(self.camera.apply_image(self.level_descs[self.over_level]), self.camera.apply_tuple(self.level_buttons[self.over_level].topright))
            else:
                self.blit(self.camera.apply_image(self.level_descs[self.over_level]), self.camera.apply_rect(self.level_descs[self.over_level].get_rect(topright = self.level_buttons[self.over_level].topleft)))
                
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

    def event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = self.camera.correct_mouse(pg.mouse.get_pos())
                if self.tower_preview_button.collidepoint(mouse_pos):
                    if self.tower_preview == None:
                        self.tower_preview = TowerPreview()
                    else:
                        self.tower_preview = None

                if self.tower_preview != None:
                    self.tower_preview.event(event)
                    return -1
                
                if self.over_level != -1:
                    return "game"
                return -1

            elif event.button == 4:
                self.camera.zoom(0.05, event.pos)

            elif event.button == 5:
                self.camera.zoom(-0.05, event.pos)

        return -1