from os import path

import pygame as pg

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 672  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 504  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 42
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

GAMEFOLDER = path.abspath("D:\\Vince\\Documents\\BSMPyGame")

PLAYER_SPEED = 300
PLAYER_IMG = "mr_denton.png"
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
