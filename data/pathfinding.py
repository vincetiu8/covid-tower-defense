import numpy
from heapq import *

def heuristic(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

class Pathfinder():
    def __init__(self, *args, **kwargs):
        self.map = [[], [], [], [], []]
        art_array = kwargs.get('arteries', None)
        if art_array == None:
            self.arteries = False
        else:
            self.map[2] = numpy.array(art_array)
            self.map[1] = numpy.array(kwargs.get('artery_entrances', None))
            self.arteries = True
        vein_array = kwargs.get('veins', None)
        if vein_array == None:
            self.veins = False
        else:
            self.map[-2] = numpy.array(vein_array)
            self.map[-1] = numpy.array(kwargs.get('vein_entrances', None))
            self.veins = True

        if self.arteries == False and self.veins == False:
            self.neighbors = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]
        else:
            self.neighbors = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, -1), (0, 0, 1)]

        self.base_map = numpy.array(kwargs.get('base_map', None))

    def clear_nodes(self, map):
        self.paths = {}
        self.flying_paths = {}
        self.map[0] = numpy.array(map)

    def set_tower_map(self, map):
        self.tower_map = map

    def astar(self, start, goals, ignore_towers):
        try:
            if ignore_towers:
                return self.flying_paths[start].copy()
            return self.paths[start].copy()

        except:
            if ignore_towers:
                temp_map = self.map[0].copy()
                self.map[0] = self.base_map

            prevstate = self.map[0][start[0][0]][start[0][1]]
            self.map[0][start[0][0]][start[0][1]] = 0

            close_set = set()
            came_from = {}

            oheap = []
            fscore = {}
            for goal in goals:
                goal_node = goal.get_node()
                fscore[goal_node] = heuristic(start[0], goal_node[0])
                heappush(oheap, (fscore[goal_node], goal_node))

            while oheap:
                current = heappop(oheap)[1]

                if current == start:
                    data = []
                    while current in came_from:
                        data.append(current)
                        current = came_from[current]
                    data.append(current)
                    self.map[0][start[0][0]][start[0][1]] = prevstate
                    if ignore_towers:
                        self.map[0] = temp_map
                        self.flying_paths[start] = data
                    else:
                        self.paths[start] = data
                    return data.copy()

                close_set.add(current)

                for i, j, k in self.neighbors:
                    neighbor = (current[0][0] + i, current[0][1] + j), current[1] + k
                    if abs(neighbor[1]) > 2:
                        continue
                    if self.arteries == False and neighbor[1] > 0:
                        continue
                    if self.veins == False and neighbor[1] < 0:
                        continue

                    cur_array = self.map[neighbor[1]]
                    tentative_g_score = fscore[current] + heuristic(current[0], neighbor[0])
                    if 0 <= neighbor[0][0] < cur_array.shape[0]:
                        if 0 <= neighbor[0][1] < cur_array.shape[1]:
                            if cur_array[neighbor[0][0]][neighbor[0][1]] == 1:
                                continue
                        else:
                            # array bound y walls
                            continue
                    else:
                        # array bound x walls
                        continue

                    if neighbor in close_set and tentative_g_score >= fscore.get(neighbor[0], 0):
                        continue

                    if tentative_g_score < fscore.get(neighbor[0], 0) or neighbor not in [i[1] for i in oheap]:
                        came_from[neighbor] = current
                        fscore[neighbor] = tentative_g_score
                        heappush(oheap, (fscore[neighbor], neighbor))

            self.paths[start] = False
            self.map[0][start[0][0]][start[0][1]] = prevstate
            return False