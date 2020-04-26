from pytmx.util_pygame import load_pygame

from data.settings import *

def tile_from_coords(i, tilesize):
    return int(round((i - tilesize / 2) / tilesize))

def tile_from_xcoords(i, tilesize):
    return int(round(i / tilesize))

def round_to_tilesize(i, tilesize):
    return tilesize * round((i - tilesize / 2) / tilesize)

def round_to_mtilesize(i, tilesize):
    return tilesize * (round((i) / tilesize) + 1 / 2)

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def clamp(x, s, b):
    return max(min(x, b), s)

class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tilesize = tm.tilewidth
        self.tmxdata = tm
        self.clear_map()

    def render(self, surface, layers):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in layers:
            try:
                for x, y, gid in self.tmxdata.get_layer_by_name(layer):
                    tile = ti(gid)
                    if tile:
                        surface.blit(pg.transform.rotate(tile, 0), (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))
            except:
                print("No layer with name " + layer)

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(temp_surface, ["background", "arteries", "veins"])
        return temp_surface

    def make_objects(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(temp_surface, ["foreground"])
        return temp_surface

    def change_node(self, x, y, state):
        if (x < 0 or x >= len(self.map) or y < 0 or y >= len(self.map[0])):
            return False
        self.map[x][y] = state
        self.valid_tower_tiles[x][y] = state - 1 # 1 --> 0, 0 --> -1

    def add_tower(self, x, y, tower):
        if (x < 0 or x >= len(self.tower_map) or y < 0 or y >= len(self.tower_map[0])):
            return False
        self.tower_map[x][y] = tower
        self.reset_valid_tower_tiles()
        
    def upgrade_tower(self, x, y):
        if (x < 0 or x >= len(self.tower_map) or y < 0 or y >= len(self.tower_map[0])):
            return False
        elif self.tower_map[x][y] == None:
            return False
        self.tower_map[x][y].upgrade()

    def remove_tower(self, x, y):
        if (x < 0 or x >= len(self.tower_map) or y < 0 or y >= len(self.tower_map[0])):
            return False
        elif self.tower_map[x][y] == None:
            return False
        self.tower_map[x][y].kill()
        self.change_node(x, y, 0)
        self.reset_valid_tower_tiles()

    def get_map(self):
        return self.map

    def get_tower_map(self):
        return self.tower_map

    def get_node(self, x, y):
        if (x < 0 or x >= len(self.map) or y < 0 or y >= len(self.map[0])):
            return -1
        return self.map[x][y]
    
    def reset_valid_tower_tiles(self):
        for x in range(len(self.valid_tower_tiles)):
            for y in range(len(self.valid_tower_tiles[0])):
                self.valid_tower_tiles[x][y] = self.map[x][y] - 1
    
    def is_valid_tower_tile(self, x, y):
        if (x < 0 or x >= len(self.valid_tower_tiles) or y < 0 or y >= len(self.valid_tower_tiles[0])):
            return False
        return self.valid_tower_tiles[x][y]
    
    def set_valid_tower_tile(self, x, y, state):
        self.valid_tower_tiles[x][y] = state

    def clear_map(self):
        self.map = [[0 for row in range(self.tmxdata.height)] for col in range(self.tmxdata.width)]
        self.tower_map = [[None for row in range(self.tmxdata.height)] for col in range(self.tmxdata.width)]
        self.valid_tower_tiles = [[-1 for row in range(self.tmxdata.height)] for col in range(self.tmxdata.width)]

class Camera():
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.current_zoom = min(width / map_width, height / map_height)
        if (width / map_width > height / map_height):
            self.short_width = True
        else:
            self.short_width = False
        self.minzoom = self.current_zoom
        self.critical_ratio = max(width / map_width, height / map_height) + 0.1
        self.camera = pg.Rect((self.width - self.map_width * (self.current_zoom + 0.05)) / 2, (self.height- self.map_height * self.current_zoom) / 2, width, height)

    def apply_tuple(self, tuple):
        return ([x * self.current_zoom + self.camera.topleft[i] for i, x in enumerate(tuple)])

    def apply_rect(self, rect):
        x = rect.x * self.current_zoom + self.camera.topleft[0]
        y = rect.y * self.current_zoom + self.camera.topleft[1]
        w = rect.w * self.current_zoom
        h = rect.h * self.current_zoom
        return pg.Rect(x, y, w, h)

    def apply_image(self, image):
        size = image.get_rect().size
        return pg.transform.scale(image, ([round(self.current_zoom * x) for x in size]))

    def correct_mouse(self, pos):
        return ([round((x - self.camera.topleft[i]) / self.current_zoom) for i, x in enumerate(pos)])

    def update(self, x, y, amount):
        self.current_zoom += amount

        newx = x - self.width / 2
        newy = y - self.height / 2

        self.camera = self.camera.move(amount * (self.map_width - self.width - newx) / 2,
                                       amount * (self.map_height - self.height - newy))


    def zoom(self, amount, pos):
        if (amount > 0 and self.current_zoom >= self.minzoom + 1 or amount < 0 and self.current_zoom <= self.minzoom):
            return


        self.update(pos[0], pos[1], amount)