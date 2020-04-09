from os import path

import pygame as pg

LIVES = 5

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
FPS = 60

SPAWN_RATE = 100

# looks for img_folder and map_folder in the same folder as the code
GAME_FOLDER = path.dirname(path.abspath(__file__))
IMG_FOLDER = path.join(GAME_FOLDER, "img")
MAP_FOLDER = path.join(GAME_FOLDER, 'maps')

ENEMY_IMG = pg.image.load(path.join(IMG_FOLDER, "corona.png"))
ANITBODY_GUN_IMG = pg.image.load(path.join(IMG_FOLDER, "antibody_gun.png"))
ANITBODY_BASE_IMG = pg.image.load(path.join(IMG_FOLDER, "antibody_base.png"))