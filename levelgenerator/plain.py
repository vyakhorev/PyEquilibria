'''
A few test setups of the world
'''

from simcubes.world import cSimWorld
from simcubes.cubes import *
from simcubes.en import Orientation

import random as rnd

def generate_grass_plain(N=10, M=10, H=1):
    '''
    :return: A single chunk, plain of grass
    '''
    TheWorld = cSimWorld()
    TheWorld.set_active_chunk(1)

    counter = 1
    for x in range(N):
        for y in range(M):
            for z in range(H):
                bl = cGrass()
                bl.set_coords(x, y, z)
                bl.set_gid(counter)
                counter += 1
                TheWorld.add_block(bl)

    return TheWorld

def generate_test_landscape():
    '''
    :return: A single chunk with some test blocks
    '''
    TheWorld = cSimWorld()
    TheWorld.set_active_chunk(1)

    counter = 1

    SIZE = 20

    # Some sand
    for x in range(SIZE):
        for y in range(SIZE):
            bl = cSand()
            bl.set_coords(x, y, 1)
            bl.set_gid(counter)
            counter += 1
            TheWorld.add_block(bl)

    # some white noise of grass
    hmp = cRandomHeightMap(SIZE, SIZE)
    hmp.generate_heights(5)
    counter = hmp.simple_spawn(TheWorld, cGrass, 2, counter)

    # # Some water on it
    # for x in range(15):
    #     for y in range(15):
    #         bl = cWater()
    #         bl.set_coords(x, y, 2)
    #         bl.set_gid(counter)
    #         counter += 1
    #         TheWorld.add_block(bl)

    # # And a small island of grass
    # for x in range(5,10):
    #     for y in range(10,15):
    #         bl = cGrass()
    #         bl.set_coords(x, y, 3)
    #         bl.set_gid(counter)
    #         counter += 1
    #         TheWorld.add_block(bl)
    #
    # # And a small island of grass
    # for x in range(6,9):
    #     for y in range(10,15):
    #         bl = cGrass()
    #         bl.set_coords(x, y, 4)
    #         bl.set_gid(counter)
    #         counter += 1
    #         TheWorld.add_block(bl)

    return TheWorld


class cHeightMap:
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

    def simple_spawn(self, world_instance, block_class, ground_level=0, counter=0):
        for x, axis_x in enumerate(self.heights):
            for y, h_i in enumerate(axis_x):
                # spawn a column of height h_i in the world
                for z in range(ground_level, h_i):
                    counter += 1
                    new_block = block_class()
                    new_block.set_coords(x, y, z)
                    new_block.set_gid(counter)
                    world_instance.add_block(new_block)
        return counter


class cRandomHeightMap(cHeightMap):
    def generate_heights(self, max_h=10):
        self.heights = []
        for x in range(0, self.N):
            this_x = []
            for y in range(0, self.M):
                this_x += [round(rnd.random()*max_h)]
            self.heights += [this_x]


class cBrownianNonCorrelatedHeightMap(cHeightMap):
    def generate_heights(self, sigma=3):
        self.heights = []
        for x in range(0, self.N):
            this_x = []
            y_i = (rnd.random()-0.5)*sigma
            for y in range(0, self.M):
                this_x += [round(y_i)]
                y_i = y_i + (rnd.random()-0.5)*sigma
            self.heights += [this_x]

class cBrownianCorrelatedHeightMap(cHeightMap):
    def generate_heights(self, sigma=5):
        self.heights = []

        trends_num = round(self.N)
        trends = []
        trend_factors = []

        for i in range(trends_num):
            tr_i = []
            t0 = (rnd.random() - 0.5) * sigma
            for y in range(0, self.M):
                t0 += (rnd.random() - 0.5) * sigma
                tr_i += [t0]
            trends += [tr_i]

            trend_factors += [rnd.random()]

        # for i, fi in enumerate(trend_factors):
        #     trend_factors[i] = fi / ((i+1)/2)

        for x in range(0, self.N):
            this_x = []
            for t, y in enumerate(range(0, self.M)):
                y_i = 0
                for i, tr_i in enumerate(trends):
                    y_i += trend_factors[i] * tr_i[t]
                this_x += [round(y_i)]
            self.heights += [this_x]

class cMidPointDisplacementHeightMap(cHeightMap):
    def generate_heights(self):
        self.heights = []




    def move_point(self, x, y, dz):
        self.heights[x][y] += dz



    def multiply_heights(self, other_heights):
        pass

    def round_heights(self):
        for x in range(0, self.N):
            for y in range(0, self.M):
                self.heights[x][y] = round(self.heights[x][y])


def generate_simple_conveyor_system():
    '''
    :return: Hand-tuned system with a box and a conveyor
    '''

    TheWorld = generate_grass_plain(5,5,1)

    box1 = cBox()
    box1.set_coords(2, 1, 1)
    box1.set_gid(100)
    box1.set_orientation(Orientation.North)
    TheWorld.add_block(box1)

    conv1 = cConveyor()
    conv1.set_coords(2, 2, 1)
    conv1.set_gid(200)
    conv1.set_orientation(Orientation.North)
    TheWorld.add_block(conv1)

    conv2 = cConveyor()
    conv2.set_coords(2, 3, 1)
    conv2.set_gid(300)
    conv2.set_orientation(Orientation.North)
    TheWorld.add_block(conv2)

    box2 = cBox()
    box2.set_coords(2, 4, 1)
    box2.set_gid(400)
    box2.set_orientation(Orientation.North)
    TheWorld.add_block(box2)

    box1.connect()
    box2.connect()
    conv1.connect()
    conv2.connect()

    return TheWorld


