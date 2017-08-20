'''
Different kind of grounds, including ores.
'''

from simcubes.world import cSimCube
from simcubes.en import CubeTypes

from simcubes.behaviours.eco import cBehBlooming, cBehTemperature, cBehChemicalContamination, cBehBioDivercity


class cGrass(cSimCube):

    def init_behaviours(self):
        self.cube_type = CubeTypes.blSoil
        self.register_behaviour(cBehBlooming(self, 15.0))
        # self.register_behaviour(cBehTemperature(self, 1.0))
        # self.register_behaviour(cBehChemicalContamination(self))
        # self.register_behaviour(cBehBioDivercity(self, 1.0))


class cWater(cSimCube):

    def init_behaviours(self):
        self.cube_type = CubeTypes.blWater
        # self.register_behaviour(cBehTemperature(self, 1.0))
        # self.register_behaviour(cBehChemicalContamination(self))
        # self.register_behaviour(cBehBioDivercity(self, 1.0))
        pass


class cSand(cSimCube):

    def init_behaviours(self):
        self.cube_type = CubeTypes.blSand
        # self.register_behaviour(cBehTemperature(self, 1.0))
        # self.register_behaviour(cBehChemicalContamination(self))
        # self.register_behaviour(cBehBioDivercity(self, 1.0))
        pass


class cRock(cSimCube):

    def init_behaviours(self):
        self.cube_type = CubeTypes.blRock
        # self.register_behaviour(cBehTemperature(self, 1.0))
        # self.register_behaviour(cBehChemicalContamination(self))
        # self.register_behaviour(cBehBioDivercity(self, 1.0))
        pass