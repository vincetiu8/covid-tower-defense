import numpy
from heapq import *

def heuristic(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

class Pathfinder():
    def __init__(self, arteries, artery_entrances, veins, vein_entrances):
        self.map = [[], [], [], [], []]
        self.map[2] = numpy.array(arteries)
        self.map[1] = numpy.array(artery_entrances)
        self.map[-2] = numpy.array(veins)
        self.map[-1] = numpy.array(vein_entrances)
        self.neighbors = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, -1), (0, 0, 1)]

    def astar(self, aray, start, goal):
        self.map[0] = numpy.array(aray)

        close_set = set()
        came_from = {}

        gscore = {start: 0}
        fscore = {start: heuristic(start[0], goal)}
        oheap = []

        heappush(oheap, (fscore[start], start))

        while oheap:

            current = heappop(oheap)[1]

            if current[0] == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                data.append(current)
                return data[::-1]

            close_set.add(current)

            for i, j, k in self.neighbors:
                neighbor = (current[0][0] + i, current[0][1] + j), current[1] + k
                if abs(neighbor[1]) > 2:
                    continue
                cur_array = self.map[neighbor[1]]
                tentative_g_score = gscore[current] + heuristic(current[0], neighbor[0])
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

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor[0], 0):
                    continue

                if tentative_g_score < gscore.get(neighbor[0], 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor[0], goal)
                    heappush(oheap, (fscore[neighbor], neighbor))

        return False