'''
Environmental threads: blooming, growing, pollution e.t.c.
'''

import logging

from simcubes.behaviours.basebehaviour import cSimulBehaviour
from simcubes.simcore import cEvent
from simcubes.en import BehComponentRoles
import random as rnd

logger = logging.getLogger(__name__)


# todo: move cBehRandomPuassonTick into a general module
# todo: make typed behaviours (with roles) general onces and ensure get_animation_data() stability


class cBehRandomPuassonTick(cSimulBehaviour):
    '''
    Random periodicity to minimise peaks in events count.
    Basic behaviour for all environments
    '''

    def __init__(self, parent, intensity=5.0):
        '''
        :param parent: block / cube / whatever
        :param intensity: mean time between two ticks
        '''
        super().__init__(parent)
        self.lam = 1.0 / intensity
        self.is_active = True

    def run(self):
        while self.is_active:
            # random timeout
            yield cEvent(self, rnd.expovariate(self.lam))
            self.do_tick()

    def do_tick(self):
        # Implement calculations here
        pass


class cBehBlooming(cBehRandomPuassonTick):
    '''
    Periodically blooming. An example.
    '''

    behaviour_role = BehComponentRoles.behBlooming

    def __init__(self, parent, intensity=5.0):
        super().__init__(parent, intensity)
        self.is_active = True
        self.is_blooming = rnd.choice([True, False])

    def get_animation_data(self):
        # Unreal engine is reponsible for unrestanding the order
        # of the tupled parameters.
        return self.is_blooming

    def do_tick(self):
        self.is_blooming = not self.is_blooming


class cBehTemperature(cBehRandomPuassonTick):
    '''
    Random walk around average temperature
    '''

    behaviour_role = BehComponentRoles.behTemperature

    def __init__(self, parent, intensity=5.0):
        super().__init__(parent, intensity)
        self.is_active = True
        # sckewed distribution of temperature
        self.av_temp = rnd.weibullvariate(1.0, 1.5)
        self.current_temperature = self.av_temp
        self.sigma = 0.1

    def get_animation_data(self):
        return self.current_temperature

    def do_tick(self):
        self.current_temperature += rnd.normalvariate(self.av_temp - self.current_temperature, self.sigma)


class cBehChemicalContamination(cBehRandomPuassonTick):
    '''
    Random initial values of C, Fe, K, O, H, N
    '''

    behaviour_role = BehComponentRoles.behChemistry

    def __init__(self, parent):
        super().__init__(parent)
        self.is_active = False  # not ticks here, nice example
        self.perc_C = rnd.weibullvariate(1.0, 1.5)
        self.perc_Fe = rnd.weibullvariate(1.0, 1.5)
        self.perc_K = rnd.weibullvariate(1.0, 1.5)
        self.perc_O = rnd.weibullvariate(1.0, 1.5)
        self.perc_H = rnd.weibullvariate(1.0, 1.5)
        self.perc_N = rnd.weibullvariate(1.0, 1.5)

    def get_animation_data(self):
        return (self.perc_C,
                self.perc_Fe,
                self.perc_K,
                self.perc_O,
                self.perc_H,
                self.perc_N)


class cBehBioDivercity(cBehRandomPuassonTick):
    '''
    Bushes, grass, trees, predators, preys - all in isolated environment
    '''

    behaviour_role = BehComponentRoles.behBiomass

    def __init__(self, parent, intensity=5.0):
        super().__init__(parent, intensity)
        self.is_active = True
        self.bushes = rnd.weibullvariate(1.0, 1.5)
        self.grass = rnd.weibullvariate(1.0, 1.5)
        self.trees = rnd.weibullvariate(1.0, 1.5)
        self.predators = rnd.weibullvariate(1.0, 1.5)
        self.preys = rnd.weibullvariate(1.0, 1.5)

    def get_animation_data(self):
        return (self.bushes,
                self.grass,
                self.trees,
                self.predators,
                self.preys)

    def do_tick(self):
        self.bushes += rnd.normalvariate(0, 0.1)
        self.grass += rnd.normalvariate(0, 0.1)
        self.trees += rnd.normalvariate(0, 0.1)
        self.predators += rnd.normalvariate(0, 0.1)
        self.preys += rnd.normalvariate(0, 0.1)
