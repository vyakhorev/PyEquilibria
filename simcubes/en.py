'''
All the enumerations in one place
'''

from enum import IntEnum


class Orientation(IntEnum):
    '''
    Defines how one block is oriented.
    '''
    West = 0    # Towards decreasing X
    East = 1    # Towards increasing X
    South = 2   # Towards decreasing Y
    North = 3   # Towards increasing Y
    Down = 4    # Towards decreasing Z
    Up = 5      # Towards increasing Y


class AliasOrientation(IntEnum):
    '''
    Same as Orientation, but in "context" of a cube
    '''
    Back = 0
    Front = 1
    Right = 2
    Left = 3
    Down = 4
    Up = 5


class Rotation(IntEnum):
    '''
    Defines how the block is oriented.
    Tooghether with Orientation this gives
    24 possibilities to place the block.
    '''
    Up = 0      # 12:00 normal, heading to the sky
    Right = 1   # 15:00 right wall on "earth"
    Down = 2    # 18:00 upside down
    Left = 3    # 21:00 left wall on "earth"



class CubeTypes(IntEnum):
    '''
    Cube types, "bl" for easier finding
    '''
    blRock = 1
    blSoil = 2
    blSand = 3
    blWater = 4


class BehComponentRoles(IntEnum):
    '''
    1 behaviour = 1 actor component in UE4.
    '''
    behBlooming = 100  # this is a trivial testing thing
    behTemperature = 1
    behVapors = 2
    behChemistry = 3
    behBiomass = 4


class ItemTypes(IntEnum):
    itWheat = 0
    itFlour = 1
    itBread = 2
    itCoal = 3
    itWater = 4


resource_volumes = {ItemTypes.itWheat: 10,
                    ItemTypes.itFlour: 3,
                    ItemTypes.itBread: 5,
                    ItemTypes.itCoal: 3,
                    ItemTypes.itWater: 5
                    }


class LiquidTypes(IntEnum):
    lqdWater = 1