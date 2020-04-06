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
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 42
GRIDWIDTH = 16
GRIDHEIGHT = 12
WIDTH = GRIDWIDTH * TILESIZE
HEIGHT = GRIDHEIGHT * TILESIZE

GAME_FOLDER = path.abspath("D:\\Vince\\Documents\\BSMPyGame")
IMG_FOLDER = path.join(GAME_FOLDER, "img")
MAP_FOLDER = path.join(GAME_FOLDER, 'maps')

ENEMY_IMG = pg.image.load(path.join(IMG_FOLDER, "corona.png"))
