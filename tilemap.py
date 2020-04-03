from pytmx.util_pygame import load_pygame

from settings import *

def tile_from_coords(i):
    return int(round((i - TILESIZE / 2) / TILESIZE))

def tile_from_xcoords(i):
    return int(round(i / TILESIZE))

def round_to_tilesize(i):
    return TILESIZE * round((i - TILESIZE / 2) / TILESIZE)


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
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
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(x, y, self.width, self.height)
