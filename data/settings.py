from os import path, listdir

import sys

import json
import pygame as pg

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

# init pygame here lol
pg.init()
pg.mixer.init()

# game settings
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

LIVES = 5
PROTEIN = 50
              
ZOOM_AMT_GAME = 0.05
ZOOM_AMT_MENU = 0.1

WAVE_DELAY = 10 # in seconds

EXPLOSION_TIME = 0.5

# define some colors (R, G, B)
WHITE = pg.Color(255, 255, 255)
CYAN = pg.Color(0, 255, 255)
BLACK = pg.Color(0, 0, 0)
DARK_GREY = pg.Color(40, 40, 40)
LIGHT_GREY = pg.Color(100, 100, 100)
GREEN = pg.Color(0, 255, 0)
DARK_GREEN = pg.Color(0, 60, 0)
RED = pg.Color(255, 0, 0)
DARK_RED = pg.Color(60, 0, 0)
YELLOW = pg.Color(255, 255, 0)
ORANGE = pg.Color(255, 127, 0)
MAROON = pg.Color(127, 0, 0)

HALF_WHITE = pg.Color(255, 255, 255, 127)
HALF_RED = pg.Color(255, 0, 0, 127)
HALF_ORANGE = pg.Color(255, 127, 0, 127)
HALF_YELLOW = pg.Color(255, 255, 0, 127)
HALF_GREEN = pg.Color(0, 255, 0, 127)
HALF_CYAN = pg.Color(0, 255, 255, 127)
HALF_BLUE = pg.Color(0, 0, 255, 127)
HALF_PURPLE = pg.Color(127, 0, 255, 127)
HALF_PINK = pg.Color(255, 0, 255, 127)

AURA_COLORS = [HALF_RED, HALF_ORANGE, HALF_YELLOW, HALF_GREEN, HALF_CYAN, HALF_BLUE, HALF_PURPLE, HALF_PINK]

# looks for img_folder and map_folder in the same folder as the code
GAME_FOLDER = resource_path("data")
IMG_FOLDER = path.join(GAME_FOLDER, "img")
MAP_FOLDER = path.join(GAME_FOLDER, 'maps')
LEVELS_FOLDER = path.join(GAME_FOLDER, "levels")
FONTS_FOLDER = path.join(GAME_FOLDER, "fonts")
AUDIO_FOLDER = path.join(GAME_FOLDER, "audio")

PATH_IMG_FOLDER = path.join(IMG_FOLDER, "path")
UI_IMG_FOLDER = path.join(IMG_FOLDER, "ui")
ENEMIES_IMG_FOLDER = path.join(IMG_FOLDER, "enemies")
TOWERS_IMG_FOLDER = path.join(IMG_FOLDER, "towers")
GAME_STOP_IMG_FOLDER = path.join(IMG_FOLDER, "game_stop")
OPTIONS_IMG_FOLDER = path.join(IMG_FOLDER, "options")
MENU_IMG_FOLDER = path.join(IMG_FOLDER, "menu")

ENEMIES_AUD_FOLDER = path.join(AUDIO_FOLDER, "enemies")
TOWERS_AUD_FOLDER = path.join(AUDIO_FOLDER, "towers")
GAME_STOP_AUD_FOLDER = path.join(AUDIO_FOLDER, "game_stop")

# init save data
with open(path.join(GAME_FOLDER, "save.json"), "r") as data_file:
    SAVE_DATA = json.load(data_file)

# init screen
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def toggle_fullscreen():
    if SAVE_DATA["fullscreen"]:
        SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
    else:
        SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
toggle_fullscreen()

# UI Constants
MENU_OFFSET = 10
MENU_OFFSET_2 = 5
MENU_TEXT_SIZE = 30

# TowerSelectMenu Constants
NUM_ALLOWED = 2
GRID_ROW_SIZE = 5
GRID_CELL_SIZE = 80 # both width and height
GRID_SEPARATION = 30
GRID_MARGIN_X = 60
GRID_MARGIN_Y = 180

GRID_2_CELL_SIZE = 50
GRID_2_SEPARATION = 30
GRID_2_MARGIN_X = 20

BTN_PADDING = 20
BTN_X_MARGIN = 100
BTN_Y = 620

# Options Constants
OPTIONS_SEPARATION = 30

TICK_BOX_SIZE = 50
SLIDER_BAR_WIDTH = 270
SLIDER_BAR_HEIGHT = 20
SLIDER_WIDTH = 20
SLIDER_HEIGHT = 50

# load ui images
HEART_IMG = pg.image.load(path.join(UI_IMG_FOLDER, "heart.png"))
PROTEIN_IMG = pg.image.load(path.join(UI_IMG_FOLDER, "protein.png"))
LEFT_ARROW_IMG = pg.image.load(path.join(UI_IMG_FOLDER, "left.png"))
RIGHT_ARROW_IMG = pg.transform.rotate(pg.image.load(path.join(UI_IMG_FOLDER, "left.png")).copy(), 180)

# Initializing the mixer in the settings file lol but rn i don't see a better way.
# Audio
HEART_BEEP_SFX = pg.mixer.Sound(path.join(GAME_STOP_AUD_FOLDER, "heart_beep.wav"))
FLATLINE_SFX = pg.mixer.Sound(path.join(GAME_STOP_AUD_FOLDER, "flatline.wav"))
BUY_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "buy_sound.wav"))

# init level data
LEVEL_DATA = []
level_list = sorted(listdir(LEVELS_FOLDER))

for file in level_list:
    with open(path.join(LEVELS_FOLDER, file)) as data_file:
        level = json.load(data_file)
        enemies = []
        for wave in level["waves"]:
            for sub_wave in wave:
                enemy = sub_wave["enemy_type"]
                if enemy not in enemies:
                    enemies.append(enemy)
        level["enemies"] = enemies
        LEVEL_DATA.append(level)

with open(path.join(GAME_FOLDER, "enemies.json"), "r") as data_file:
    ENEMY_DATA = json.load(data_file)
    for enemy in ENEMY_DATA:
        ENEMY_DATA[enemy]["image"] = pg.image.load(path.join(ENEMIES_IMG_FOLDER, "{}.png".format(enemy)))
        ENEMY_DATA[enemy]["death_sound"] = pg.mixer.Sound(path.join(ENEMIES_AUD_FOLDER, "{}.wav".format(enemy)))

# load tower data
with open(path.join(GAME_FOLDER, "towers.json"), "r") as data_file:
    TOWER_DATA = json.load(data_file)
    for tower in TOWER_DATA:
        for stage in range(3):
            TOWER_DATA[tower]["stages"][stage]["base_image"] = pg.image.load(path.join(TOWERS_IMG_FOLDER, tower + "_base" + str(stage) + ".png"))
            TOWER_DATA[tower]["stages"][stage]["shoot_sound"] = pg.mixer.Sound(path.join(TOWERS_AUD_FOLDER, "{}.wav".format(tower)))
            
            temp_base = TOWER_DATA[tower]["stages"][stage]["base_image"].copy()
            base = TOWER_DATA[tower]["stages"][stage]["base_image"]
            if not TOWER_DATA[tower]["stages"][stage]["area_of_effect"]:
                TOWER_DATA[tower]["stages"][stage]["bullet_image"] = pg.image.load(
                    path.join(TOWERS_IMG_FOLDER, tower + "_bullet" + str(stage) + ".png"))

                if TOWER_DATA[tower]["stages"][stage]["rotating"]:
                    TOWER_DATA[tower]["stages"][stage]["gun_image"] = pg.image.load(
                        path.join(TOWERS_IMG_FOLDER, tower + "_gun" + str(stage) + ".png"))
                    temp_base.blit(TOWER_DATA[tower]["stages"][stage]["gun_image"],
                               TOWER_DATA[tower]["stages"][stage]["gun_image"].get_rect(center = base.get_rect().center))
            
            TOWER_DATA[tower]["stages"][stage]["image"] = temp_base


with open(path.join(GAME_FOLDER, "attributes.json"), "r") as data_file:
    ATTR_DATA = json.load(data_file)
    
# Update audio volume
def update_sfx_vol():
    vol = SAVE_DATA["sfx_vol"]
    HEART_BEEP_SFX.set_volume(vol * 0.75)
    FLATLINE_SFX.set_volume(vol * 0.75)
    BUY_SFX.set_volume(vol)
    
    for tower in TOWER_DATA:
        for stage in range(3):
            TOWER_DATA[tower]["stages"][stage]["shoot_sound"].set_volume(vol)
            
    for enemy in ENEMY_DATA:
        ENEMY_DATA[enemy]["death_sound"].set_volume(vol)
        
update_sfx_vol()

# load path images
PATH_VERTICAL_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "vertical.png"))
PATH_HORIZONTAL_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "horizontal.png"))
PATH_CORNER1_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "corner1.png"))
PATH_CORNER2_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "corner2.png"))
PATH_CORNER3_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "corner3.png"))
PATH_CORNER4_IMG = pg.image.load(path.join(PATH_IMG_FOLDER, "corner4.png"))

# load options images
BRAIN_IMG = pg.image.load(path.join(OPTIONS_IMG_FOLDER, "brain.png"))
OPTIONS_IMGS = [None, None]
OPTIONS_BACK_IMGS = [None, None]

for i, to_concat in enumerate(["", "_hover"]):
    OPTIONS_IMGS[i] = pg.image.load(path.join(OPTIONS_IMG_FOLDER, "options{}.png".format(to_concat)))
    OPTIONS_BACK_IMGS[i] = pg.image.load(path.join(OPTIONS_IMG_FOLDER, "back_btn{}.png".format(to_concat)))

# load other images
START_SCREEN_IMG = pg.transform.scale(pg.image.load(path.join(MENU_IMG_FOLDER, "start_screen.png")), (720, 720))
LEVEL_BUTTON_IMG = pg.image.load(path.join(MENU_IMG_FOLDER, "level_button.png"))
LOCK_IMG = pg.image.load(path.join(MENU_IMG_FOLDER, "lock.png"))
BODY_IMG = pg.transform.scale(pg.image.load(path.join(MENU_IMG_FOLDER, "body.png")), (1920, 2610))

# load game over images
RESTART_BTN_IMGS = [[None, None], [None, None]]
BACK_BTN_IMGS = [[None, None], [None, None]]
RESUME_BTN_IMGS = [None, None]

for i, to_concat_1 in enumerate(["", "_lost"]):
    for j, to_concat_2 in enumerate(["", "_hover"]):
        RESTART_BTN_IMGS[i][j] = pg.image.load(path.join(GAME_STOP_IMG_FOLDER, "restart_btn{}{}.png".format(to_concat_1, to_concat_2)))
        BACK_BTN_IMGS[i][j] = pg.image.load(path.join(GAME_STOP_IMG_FOLDER, "back_btn{}{}.png".format(to_concat_1, to_concat_2)))
        
        if i == 0:
            RESUME_BTN_IMGS[j] = pg.image.load(path.join(GAME_STOP_IMG_FOLDER, "resume_btn{}.png".format(to_concat_2)))
        
HEART_MONITOR_NORMAL_IMG = pg.image.load(path.join(GAME_STOP_IMG_FOLDER, "heart_monitor_normal.png"))
HEART_MONITOR_FLATLINE_IMG = pg.image.load(path.join(GAME_STOP_IMG_FOLDER, "heart_monitor_flatline.png"))

# load fonts path
FONT = path.join(FONTS_FOLDER, "mini_pixel-7.ttf")

DNA_ON_FINISH = 100
TOWER_PURCHASE_COST = 100