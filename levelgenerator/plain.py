'''
A few test setups of the world
'''

from simcubes.world import cSimWorld
from simcubes.cubes import *
from simcubes.en import Orientation
from levelgenerator.heightmaps import cRandomHeightMap, cDiamondSquareHeightMap


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
    TheWorld = cSimWorld()
    TheWorld.set_active_chunk(1)

    counter = 1

    SIZE = 50

    hmp = cDiamondSquareHeightMap(SIZE, SIZE)
    hmp.generate_heights()
    counter = hmp.four_elements_spawn(TheWorld, ground_level=2, counter=counter)
    return TheWorld




def generate_simple_conveyor_system():
    '''
    A case to test autoconnection
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


