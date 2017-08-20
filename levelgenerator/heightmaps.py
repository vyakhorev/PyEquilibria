
import random as rnd
import math
from simcubes.cubes.grounds import cGrass, cRock, cSand, cWater


class cHeightMap:
    '''
    Represents heights in a box
    '''

    def __init__(self, N=20, M=20):
        self.N = N
        self.M = M
        self.heights = None


    def init_heights(self):
        self.heights = []
        for x in range(0, self.N):
            this_x = []
            for y in range(0, self.M):
                this_x += [0]
            self.heights += [this_x]

    def generate_heights(self):
        self.init_heights()

    def set_point_height(self, x, y, h):
        self.heights[y][x] = h

    def get_point_height(self, x, y):
        return self.heights[y][x]

    def get_max_height(self):
        v = 0
        for x, y in self.iterate_square_coords():
            v = max(v, self.get_point_height(x, y))
        return v

    def get_min_height(self):
        v = 0
        for x, y in self.iterate_square_coords():
            v = min(v, self.get_point_height(x, y))
        return v

    def iterate_square_coords(self):
        for x in range(0, self.N):
            for y in range(0, self.M):
                yield x, y

    def iterate_cube_coords(self, ground_level=1):
        # ensure no holes (=ground)
        for z in range(0, ground_level):
            for x in range(0, self.N):
                for y in range(0, self.M):
                    yield x, y, z

        # the rest confirmes with height values (on top, no the net of ground)
        for x, axis_x in enumerate(self.heights):
            for y, h_i in enumerate(axis_x):
                # spawn a column of height h_i in the world
                for z in range(ground_level, h_i):
                    yield x, y, z

    def simple_spawn(self, world_instance, block_class, ground_level = 1, counter=0):
        for x, y, z in self.iterate_cube_coords(ground_level):
            counter += 1
            new_block = block_class()
            new_block.set_coords(x, y, z)
            new_block.set_gid(counter)
            world_instance.add_block(new_block)
        return counter

    def four_elements_spawn(self, world_instance, ground_level = 1, counter=0):
        max_level = self.get_max_height()
        min_level = max(self.get_min_height(), ground_level)

        # Solid rocks in the lower level
        for z in range(0, ground_level):
            for x in range(0, self.N):
                for y in range(0, self.M):
                    counter += 1
                    new_block = cRock()
                    new_block.set_coords(x, y, z)
                    new_block.set_gid(counter)
                    world_instance.add_block(new_block)

        # Fill the grounds. Surface of soil is of random thickness.
        water_level = round(0.8 * (max_level + min_level) / 2)
        for x, axis_x in enumerate(self.heights):
            for y, h_i in enumerate(axis_x):
                # spawn a column of height h_i in the world
                if h_i > 0:
                    soil_expectation = (max_level - min_level) / h_i * 5.0
                else:
                    soil_expectation = 1.0
                soil_thickness = round(rnd.weibullvariate(soil_expectation, 1.5))

                for z in range(ground_level, h_i):
                    if z > h_i - soil_thickness:
                        if z < water_level * 1.1:
                            # soil sand 50/50 near and below water
                            if rnd.random() > 0.5:
                                new_block = cGrass()
                            else:
                                new_block = cSand()
                        else:
                            new_block = cGrass()
                    else:
                        new_block = cRock()
                    counter += 1
                    new_block.set_coords(x, y, z)
                    new_block.set_gid(counter)
                    world_instance.add_block(new_block)

                # Fill the empty space below the level with water
                for z in range(h_i, water_level):
                    if z>=ground_level:
                        new_block = cWater()
                        counter += 1
                        new_block.set_coords(x, y, z)
                        new_block.set_gid(counter)
                        world_instance.add_block(new_block)

        return counter


class cRandomHeightMap(cHeightMap):
    '''
    Random heights everywhere
    '''

    def generate_heights(self, max_h=10):
        self.heights = []
        for x in range(0, self.N):
            this_x = []
            for y in range(0, self.M):
                this_x += [round(rnd.random()*max_h)]
            self.heights += [this_x]


class cDiamondSquareHeightMap(cHeightMap):
    '''
    https://en.wikipedia.org/wiki/Diamond-square_algorithm
    '''

    def __init__(self, N, M):
        # # This is a raw generator
        # import sys
        # sys.setrecursionlimit(2000)
        # H influence a lot
        self.H = 0.8  # Hurst
        self.S = round(N / 2.0) * 1.0  # Sigma
        self.Ro = math.pow(1-math.pow(2,2*self.H-2), 0.5)
        self.offset = 5 # Z offset
        super().__init__(N, M)


    def generate_heights(self):
        self.init_heights()
        self._init_corners()
        self.diamond_step((0, 0),
                          (0, self.M-1),
                          (self.N-1, 0),
                          (self.N-1, self.M-1),
                          0)
        self.offset_heights(self.offset)
        self.round_heights()

    def _init_corners(self):
        level = 1
        magnitude = 1 / (math.pow(2, level * self.H)) * self.S * self.Ro
        self.set_point_height(0, 0, rnd.gauss(0, magnitude))
        self.set_point_height(0, self.M-1, rnd.gauss(0, magnitude))
        self.set_point_height(self.N-1, 0, rnd.gauss(0, magnitude))
        self.set_point_height(self.N-1, self.M-1, rnd.gauss(0, magnitude))

    # recursion calls

    def diamond_step(self, x0y0, x0y1, x1y0, x1y1, level):
        # self.calls+=1
        # if self.calls >= self.max_calls: return

        if (abs(x0y0[0] - x1y1[0]) <= 1) or (abs(x0y0[1] - x1y1[1]) <= 1):
            return  #recursion exit

        edges = 0

        if (0 <= x0y0[0] <= self.N - 1) and (0 <= x0y0[1] <= self.M - 1):
            h1 = self.heights[x0y0[1]][x0y0[0]]
            edges+=1
        else:
            h1 =0
        if (0 <= x0y1[0] <= self.N - 1) and (0 <= x0y1[1] <= self.M - 1):
            h2 = self.heights[x0y1[1]][x0y1[0]]
            edges += 1
        else:
            h2 =0
        if (0 <= x1y0[0] <= self.N - 1) and (0 <= x1y0[1] <= self.M - 1):
            h3 = self.heights[x1y0[1]][x1y0[0]]
            edges += 1
        else:
            h3 =0
        if (0 <= x1y1[0] <= self.N - 1) and (0 <= x1y1[1] <= self.M - 1):
            h4 = self.heights[x1y1[1]][x1y1[0]]
            edges += 1
        else:
            h4 =0

        x = round((x0y0[0] + x1y0[0]) / 2)
        y = round((x1y0[1] + x1y1[1]) / 2)

        if (0 <= x <= self.N-1) and (0 <= y <= self.M-1):
            magnitude = 1 / (math.pow(2, level*self.H)) * self.S * self.Ro
            new_h = (h1 + h2 + h3 + h4) / edges + rnd.gauss(0, magnitude)
            self.set_point_height(x, y, new_h)
        else:
            return  # recursion exit

        # recursion branches
        self.square_step(x0y0, (x, y), x0y1, (round((x0y0[0] - x1y0[0]) / 2) ,y), level+1)  # left
        self.square_step(x1y0, (round((x1y0[0] + x1y1[0]) / 2), y), x1y1, (x, y), level+1)  # right
        self.square_step((x, y), x1y1, (x, round((x0y1[1] + x1y1[1]) / 2)), x0y1, level+1)  # bottom
        self.square_step((x, round((x0y0[1] + x1y0[1]) / 2)), x1y0, (x, y), x0y0, level+1)  # top


    def square_step(self, v0, v90, v180, v270, level):
        # self.calls += 1
        # if self.calls >= self.max_calls: return

        if (abs(v0[1] - v180[1]) <= 1) or (abs(v90[0] - v270[0]) <= 1):
            return  #recursion exit

        edges = 0
        if (0 <= v0[0] <= self.N - 1) and (0 <= v0[1] <= self.M - 1):
            h1 = self.heights[v0[1]][v0[0]]
            edges += 1
        else:
            h1 =0
        if (0 <= v90[0] <= self.N - 1) and (0 <= v90[1] <= self.M - 1):
            h2 = self.heights[v90[1]][v90[0]]
            edges += 1
        else:
            h2 =0
        if (0 <= v180[0] <= self.N - 1) and (0 <= v180[1] <= self.M - 1):
            h3 = self.heights[v180[1]][v180[0]]
            edges += 1
        else:
            h3 =0
        if (0 <= v270[0] <= self.N - 1) and (0 <= v270[1] <= self.M - 1):
            h4 = self.heights[v270[1]][v270[0]]
            edges += 1
        else:
            h4 =0

        x = round((v270[0] + v90[0]) / 2)
        y = round((v0[1] + v180[1]) / 2)

        if (0 <= x <= self.N-1) and (0 <= y <= self.M-1):
            magnitude = 1 / (math.pow(2, level)) * self.S * self.Ro
            new_h = (h1 + h2 + h3 + h4) / edges + rnd.gauss(0, magnitude)
            self.set_point_height(x, y, new_h)
        else:
            return  # recursion exit

        # recursion branches
        self.diamond_step((v270[0], v0[1]), v270, v0, (x, y), level+1)
        self.diamond_step(v0, (x,y), (v90[0], v0[1]), v90, level+1)
        self.diamond_step((x,y), v180, v90, (v90[0], v180[1]), level+1)
        self.diamond_step(v270, (v270[0], v180[1]), (x, y), v180, level+1)

    # filters

    def offset_heights(self, offset = 10):
        for x in range(0, self.N):
            for y in range(0, self.M):
                self.set_point_height(x, y, self.heights[y][x] + offset)


    def round_heights(self):
        for x in range(0, self.N):
            for y in range(0, self.M):
                self.set_point_height(x, y, round(self.heights[y][x]))