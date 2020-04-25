import pygame as pg
from data.main import Game
from data.tilemap import *
from data.pathfinding import *
from data.game import *
from os import path
from data.settings import *

class Tower_Preview(Game):
    def __init__(self, width, height):
        self.map = TiledMap(path.join(MAP_FOLDER, "tower_test.tmx"))
        self.width = width
        self.height = height
        super().load_data()
        self.new()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.obstacles = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.goal_sprites = pg.sprite.Group()

        self.map.clear_map()

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "start":
                self.start = pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        self.map.set_valid_tower_tile(tile_from_xcoords(tile_object.x, self.map.tilesize) + i,
                                                      tile_from_xcoords(tile_object.y, self.map.tilesize) + j,
                                                      0)  # make start tile a wall so you can't place a tower on it
                        # this does not affect the path finding algo
            if tile_object.name == "goal":
                for i in range(tile_from_xcoords(tile_object.width, self.map.tilesize)):
                    for j in range(tile_from_xcoords(tile_object.height, self.map.tilesize)):
                        goal = Goal(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                        self.goal = ((round(goal.rect.x / self.map.tilesize) + i,
                                            round(goal.rect.y / self.map.tilesize) + j), 0)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)

        self.camera = Camera(self.width, self.height, self.map.width, self.map.height)
        self.pathfinder = Pathfinder()
        self.pathfinder.clear_nodes(self.map.get_map())

    def draw(self, surface):
        surface.fill((0, 0, 0))

        surface.blit(self.camera.apply_image(self.map_img), self.camera.apply_rect(self.map_rect))

        pg.draw.rect(surface, GREEN, self.camera.apply_rect(self.start.rect))
        pg.draw.rect(surface, GREEN, self.camera.apply_rect(self.goal.rect))

        for tower in self.towers:
            rotated_image = pg.transform.rotate(tower.gun_image, tower.rotation)
            new_rect = rotated_image.get_rect(center=tower.rect.center)
            surface.blit(self.camera.apply_image(rotated_image), self.camera.apply_rect(new_rect))

        for enemy in self.enemies:
            surface.blit(self.camera.apply_image(enemy.image), self.camera.apply_rect(enemy.rect))
            pg.draw.rect(surface, GREEN, self.camera.apply_rect(enemy.get_hp_rect()))

        for projectile in self.projectiles:
            surface.blit(self.camera.apply_image(projectile.image), self.camera.apply_rect(projectile.rect))

        return surface