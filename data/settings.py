from os import path, listdir, mkdir

import sys

import json
import pygame as pg

### PLACE USEREVENT USAGE HERE ###
# USEREVENT --> game over event in Game()
# USEREVENT + 1 --> timer event in DevUI()
# USEREVENT + 2 --> fade out done event in Pause()

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

def clean_title(string): # Removes underscores, capitalizes it properly
    return " ".join(string.split("_")).title()

# init pygame here lol
pg.mixer.pre_init(buffer = 2048) # initialize mixer first to reduce delays
pg.mixer.init()
pg.init()

# game settings
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
              
ZOOM_AMT_GAME = 0.05
ZOOM_AMT_MENU = 0.1

DNA_ON_COMPLETION = (50, 55, 60)
DNA_ON_PROTEIN_GOAL = (10, 15, 20)

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

BLANK = pg.Color(0, 0, 0, 0)

AURA_COLORS = [HALF_RED, HALF_ORANGE, HALF_YELLOW, HALF_GREEN, HALF_CYAN, HALF_BLUE, HALF_PURPLE, HALF_PINK]

# looks for img_folder and map_folder in the same folder as the code
GAME_FOLDER = resource_path("data")
IMG_FOLDER = path.join(GAME_FOLDER, "img")
MAP_FOLDER = path.join(GAME_FOLDER, 'maps')
LEVELS_FOLDER = path.join(GAME_FOLDER, "levels")
FONTS_FOLDER = path.join(GAME_FOLDER, "fonts")
AUDIO_FOLDER = path.join(GAME_FOLDER, "audio")
MISC_FOlDER = path.join(GAME_FOLDER, "misc")

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
MUSIC_FOLDER = path.join(AUDIO_FOLDER, "music")

# init save data
dir = path.join(path.expanduser("~"), ".sergeant_t_cell")
SAVE_FILEPATH = path.join(dir, "save.json")
SAVE_DATA = None
try:
    with open(SAVE_FILEPATH, "r") as data_file:
        SAVE_DATA = json.load(data_file)
except FileNotFoundError:
    with open(path.join(GAME_FOLDER, "starting_save.json"), "r") as data_file:
        SAVE_DATA = json.load(data_file)
    
    try:
        with open(SAVE_FILEPATH, "w") as out_file:
            json.dump(SAVE_DATA, out_file, indent=4)
    except FileNotFoundError:
        mkdir(dir)
        with open(SAVE_FILEPATH, "w") as out_file:
            json.dump(SAVE_DATA, out_file, indent=4)

SCREEN = pg.display.set_mode((SAVE_DATA["width"], SAVE_DATA["width"] * 9 // 16))
SCREEN_SIZES = [640, 854, 960, 1280, 1366, 1536, 1600, 1920, 2560, 3200, 3840]

def toggle_fullscreen():
    if SAVE_DATA["fullscreen"]:
        SCREEN = pg.display.set_mode((SAVE_DATA["width"], SAVE_DATA["width"] * 9 // 16), pg.FULLSCREEN)
    else:
        SCREEN = pg.display.set_mode((SAVE_DATA["width"], SAVE_DATA["width"] * 9 // 16))
        
toggle_fullscreen()

# Menu Constant
BODY_PARTS = { # All of these are relative to the body
    "mouth":            (652, 369),
    "esophagus":        (470, 502),
    "trachea":          (472, 643),
    "lungs":            (580, 712),
    "stomach":          (597, 1134),
    "liver":            (455, 1095),
    "gall_bladder":     (334, 1186),
    "pancreas":         (400, 1202),
    "small_intestine":  (494, 1451),
    "large_intestine":  (323, 1611),
    "anus":             (477, 1721),
    "bronchus":         (346, 862),
    "heart":            (497, 857),
    "brain":            (488, 106),
}
MAX_ENEMIES_IN_ROW = 7

# UI Constants
MENU_OFFSET = 10
MENU_OFFSET_2 = 5
MENU_TEXT_SIZE = 30

# TowerSelectMenu Constants
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
# SFX
HEART_BEEP_SFX = pg.mixer.Sound(path.join(GAME_STOP_AUD_FOLDER, "heart_beep.wav"))
FLATLINE_SFX = pg.mixer.Sound(path.join(GAME_STOP_AUD_FOLDER, "flatline.wav"))
BUY_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "buy_sound.wav"))
WRONG_SELECTION_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "wrong_selection.wav"))
TEXT_SCROLL_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "text_scroll.wav"))
BTN_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "btn.wav"))
BTN_2_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "btn2.wav"))
LEVEL_CLEAR_SFX = pg.mixer.Sound(path.join(AUDIO_FOLDER, "level_clear.wav"))

# Music
MENU_MUSIC = path.join(MUSIC_FOLDER, "643418_Beatem-up-Level-8-bit.ogg")
MILD_LEVEL_MUSIC = [path.join(MUSIC_FOLDER, "603041_Dig-It.ogg"), path.join(MUSIC_FOLDER, "923539_Adventure-Battle.ogg")]
ACUTE_LEVEL_MUSIC = [path.join(MUSIC_FOLDER, "643430_Fast-Level-8-bit.ogg"), path.join(MUSIC_FOLDER, "336068_8_bit_Challenge.ogg")]
SEVERE_LEVEL_MUSIC = [path.join(MUSIC_FOLDER, "525911_Chaos.ogg"), path.join(MUSIC_FOLDER, "367084_8_bit_Boss_Battle_4.ogg")]
LATE_SEVERE_MUSIC_LOOP = path.join(MUSIC_FOLDER, "367084_8_bit_Boss_Battle_4_loop.ogg")

# init level data
LEVEL_DATA = []
level_list = listdir(LEVELS_FOLDER)
level_list.sort()

for file in level_list:
    with open(path.join(LEVELS_FOLDER, file)) as data_file:
        level = json.load(data_file)
        enemies = [[] for i in range(3)]
        for i, stage in enumerate(level["waves"]):
            for wave in stage:
                for sub_wave in wave:
                    enemy = sub_wave["enemy_type"]
                    if enemy not in enemies[i]:
                        enemies[i].append(enemy)
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
            
            if TOWER_DATA[tower]["stages"][stage]["area_of_effect"]:
                if TOWER_DATA[tower]["stages"][stage]["aoe_buff"]:
                    continue
                
            TOWER_DATA[tower]["stages"][stage]["shoot_sound"] = pg.mixer.Sound(path.join(TOWERS_AUD_FOLDER, "{}.wav".format(tower)))


with open(path.join(GAME_FOLDER, "attributes.json"), "r") as data_file:
    ATTR_DATA = json.load(data_file)
    
# Update audio volume
def update_sfx_vol():
    vol = SAVE_DATA["sfx_vol"]
    HEART_BEEP_SFX.set_volume(vol * 0.75)
    FLATLINE_SFX.set_volume(vol * 0.75)
    BUY_SFX.set_volume(vol)
    WRONG_SELECTION_SFX.set_volume(vol * 1.2)
    TEXT_SCROLL_SFX.set_volume(vol * 0.9)
    BTN_SFX.set_volume(vol)
    BTN_2_SFX.set_volume(vol * 0.5)
    LEVEL_CLEAR_SFX.set_volume(vol)
    
    for tower in TOWER_DATA:
        for stage in range(3):
            if TOWER_DATA[tower]["stages"][stage].get("shoot_sound"):
                TOWER_DATA[tower]["stages"][stage]["shoot_sound"].set_volume(vol)
            
    for enemy in ENEMY_DATA:
        ENEMY_DATA[enemy]["death_sound"].set_volume(vol)

def update_music_vol():
    vol = SAVE_DATA["music_vol"]
    pg.mixer.music.set_volume(vol)

update_sfx_vol()
update_music_vol()

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
LEVEL_BUTTON_IMG = pg.image.load(path.join(MENU_IMG_FOLDER, "button.png"))
DARK_LEVEL_BUTTON_IMG = LEVEL_BUTTON_IMG.copy()
DARK_LEVEL_BUTTON_IMG.fill(LIGHT_GREY, special_flags=pg.BLEND_RGB_MULT)
LEVEL_BUTTON_IMG_2 = pg.transform.scale(pg.image.load(path.join(MENU_IMG_FOLDER, "level_button.png")), (64, 64))
LOCK_IMG = pg.image.load(path.join(MENU_IMG_FOLDER, "lock.png"))
BODY_IMG = pg.transform.scale(pg.image.load(path.join(MENU_IMG_FOLDER, "body.png")), (965, 1800))
VS_IMG = pg.image.load(path.join(MENU_IMG_FOLDER, "vs_sign.png"))

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

WAVE_DELAY = 10
EXPLOSION_TIME = 0.25
REFUND_AMOUNT = 0.5

TARGET_OPTIONS = {
    0: "First",
    1: "Last",
    2: "Strong",
    3: "Weak"
}
