from pytmx.util_pygame import load_pygame

from settings import *

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
        self.map = [[0 for row in range(tm.height)] for col in range(tm.width)]

    def render(self, surface, layers):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in layers:
            for x, y, gid in self.tmxdata.get_layer_by_name(layer):
                tile = ti(gid)
                if tile:
                    surface.blit(tile, (x * self.tmxdata.tilewidth,
                                        y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(temp_surface, ["background"])
        return temp_surface

    def make_objects(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA, 32).convert_alpha()
        self.render(temp_surface, ["foreground"])
        return temp_surface

    def change_node(self, x, y, state):
        if (x < 0 or x > self.width or y < 0 or y > self.height):
            return False
        self.map[x][y] = state

    def get_map(self):
        return self.map


class Camera:
    def __init__(self, map, width, height):
        self.width = width
        self.height = height
        self.map_width = map.width
        self.map_height = map.height
        self.current_zoom = min(width / map.width, height / map.height)
        self.minzoom = self.current_zoom
        self.critical_ratio = max(width / map.width, height / map.height) + 0.1
        print(self.critical_ratio)
        self.update(width / 2, height / 2)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def apply_image(self, image):
        size = image.get_rect().size
        return pg.transform.scale(image, ([round(self.current_zoom * x) for x in size]))

    def update(self, x, y):
        if (self.current_zoom < self.critical_ratio):
            newx = 0
            newy = 0

        else:
            percentage = (self.current_zoom - self.critical_ratio) / (self.minzoom + 1 - self.critical_ratio)
            maxw = self.map_width * self.current_zoom - self.width
            maxh = self.map_height * self.current_zoom - self.height
            newx = clamp(percentage * (x - self.width / 2) * self.current_zoom, -maxw, maxw)
            newy = clamp(percentage * (y - self.height / 2) * self.current_zoom, -maxh, maxh)
        adjwidth = (self.width - newx - self.map_width * self.current_zoom) / 2
        adjheight = (self.height - newy - self.map_height * self.current_zoom) / 2
        self.camera = pg.Rect(adjwidth, adjheight, self.width, self.height)

    def zoom(self, amount, pos):
        if (amount > 0 and self.current_zoom >= self.minzoom + 1 or amount < 0 and self.current_zoom <= self.minzoom):
            return

        self.current_zoom += amount
        self.update(pos[0], pos[1])
