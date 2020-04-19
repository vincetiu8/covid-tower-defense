from os import path

import json
import pygame as pg

LIVES = 5
PROTEIN = 50
              
ZOOM_AMOUNT = 0.05

# define some colors (R, G, B)
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
DARKGREY = pg.Color(40, 40, 40)
LIGHTGREY = pg.Color(100, 100, 100)
GREEN = pg.Color(0, 255, 0)
RED = pg.Color(255, 0, 0)
YELLOW = pg.Color(255, 255, 0)
HALF_WHITE = pg.Color(255, 255, 255, 127)
HALF_RED = pg.Color(255, 0, 0, 127)

# game settings
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SPAWN_RATE = 1

# looks for img_folder and map_folder in the same folder as the code
GAME_FOLDER = path.dirname(path.abspath(__file__))
IMG_FOLDER = path.join(GAME_FOLDER, "img")
MAP_FOLDER = path.join(GAME_FOLDER, 'maps')
LEVELS_FOLDER = path.join(GAME_FOLDER, "levels")
FONTS_FOLDER = path.join(GAME_FOLDER, "fonts")

PATH_FOLDER = path.join(IMG_FOLDER, "path")
UI_FOLDER = path.join(IMG_FOLDER, "ui")
ENEMIES_FOLDER = path.join(IMG_FOLDER, "enemies")
TOWERS_FOLDER = path.join(IMG_FOLDER, "towers")

# load ui images
HEART_IMG = pg.image.load(path.join(UI_FOLDER, "heart.png"))
PROTEIN_IMG = pg.image.load(path.join(UI_FOLDER, "protein.png"))
LEFT_ARROW_IMG = pg.image.load(path.join(UI_FOLDER, "left.png"))
RIGHT_ARROW_IMG = pg.transform.rotate(pg.image.load(path.join(UI_FOLDER, "left.png")).copy(), 180)

# load level data
SAMPLE_LEVEL_DATA = path.join(LEVELS_FOLDER, "sample.json")

# load enemy data
with open(path.join(GAME_FOLDER, "enemies.json"), "r") as data_file:
    ENEMY_DATA = json.load(data_file)
    for enemy in ENEMY_DATA:
        ENEMY_DATA[enemy]["image"] = pg.image.load(path.join(ENEMIES_FOLDER, ENEMY_DATA[enemy]["image"]))

# load tower data
with open(path.join(GAME_FOLDER, "towers.json"), "r") as data_file:
    TOWER_DATA = json.load(data_file)
    for tower in TOWER_DATA:
        for level in range(3):
            TOWER_DATA[tower][level]["gun_image"] = pg.image.load(path.join(TOWERS_FOLDER, tower + "_gun" + str(level) + ".png"))
            TOWER_DATA[tower][level]["base_image"] = pg.image.load(path.join(TOWERS_FOLDER, tower + "_base" + str(level) + ".png"))
            TOWER_DATA[tower][level]["bullet_image"] = pg.image.load(path.join(TOWERS_FOLDER, tower + "_bullet" + str(level) + ".png"))

# load path images
PATH_VERTICAL_IMG = pg.image.load(path.join(PATH_FOLDER, "vertical.png"))
PATH_HORIZONTAL_IMG = pg.image.load(path.join(PATH_FOLDER, "horizontal.png"))
PATH_CORNER1_IMG = pg.image.load(path.join(PATH_FOLDER, "corner1.png"))
PATH_CORNER2_IMG = pg.image.load(path.join(PATH_FOLDER, "corner2.png"))
PATH_CORNER3_IMG = pg.image.load(path.join(PATH_FOLDER, "corner3.png"))
PATH_CORNER4_IMG = pg.image.load(path.join(PATH_FOLDER, "corner4.png"))

# load other images
START_SCREEN_IMG = pg.image.load(path.join(IMG_FOLDER, "start_screen.png"))
LEVEL_BUTTON_IMG = pg.image.load(path.join(IMG_FOLDER, "level_button.png"))
RESTART_BTN_IMG = pg.image.load(path.join(IMG_FOLDER, "restart_btn.png"))
RESTART_BTN_HOVER_IMG = pg.image.load(path.join(IMG_FOLDER, "restart_btn_hover.png"))
BACK_BTN_IMG = pg.image.load(path.join(IMG_FOLDER, "back_btn.png"))
BACK_BTN_HOVER_IMG = pg.image.load(path.join(IMG_FOLDER, "back_btn_hover.png"))

# load fonts path
GAME_OVER_FONT = path.join(FONTS_FOLDER, "mini_pixel-7.ttf")
