import pygame as pg
from data.main import Game
from data.tilemap import TiledMap
from os import path
from data.settings import *

class Tower_Preview(Game):
    def __init__(self):
        self.map = TiledMap(path.join(MAP_FOLDER, "tower_test.tmx"))
        super().load_data()

