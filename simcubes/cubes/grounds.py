'''
Different kind of grounds, including ores.
'''

from simcubes.world import cSimCube
from simcubes.en import CubeTypes

from simcubes.behaviours.eco import cBehBlooming, cBehTemperature, cBehChemicalContamination, cBehBioDivercity


class cGrass(cSimCube):
    cube_type = CubeTypes.blSoil

    def init_behaviours(self):
        self.register_behaviour(cBehBlooming(self, 1.0))
        self.register_behaviour(cBehTemperature(self, 1.0))
        self.register_behaviour(cBehChemicalContamination(self))
        self.register_behaviour(cBehBioDivercity(self, 1.0))


class cWater(cSimCube):
    cube_type = CubeTypes.blWater

    def init_behaviours(self):
        self.register_behaviour(cBehTemperature(self, 1.0))
        self.register_behaviour(cBehChemicalContamination(self))
        self.register_behaviour(cBehBioDivercity(self, 1.0))


class cSand(cSimCube):
    cube_type = CubeTypes.blSand

    def init_behaviours(self):
        self.register_behaviour(cBehTemperature(self, 1.0))
        self.register_behaviour(cBehChemicalContamination(self))
        self.register_behaviour(cBehBioDivercity(self, 1.0))


class cRock(cSimCube):
    cube_type = CubeTypes.blRock

    def init_behaviours(self):
        self.register_behaviour(cBehTemperature(self, 1.0))
        self.register_behaviour(cBehChemicalContamination(self))
        self.register_behaviour(cBehBioDivercity(self, 1.0))