'''
Each cube is represented by an actor in the game. The concrete simulation
logic is set by behaviours (which are not exposed to the game engine).
However, each cube type is enumerated. The enum replication is below
(would be cool to have it in one single place).

Concrete cubes are constructed by setting their types and adding behaviours.
There is no need for subclassing.
'''

from simcubes.cubes.grounds import *
from simcubes.cubes.stashes import *
from simcubes.cubes.transport import *

