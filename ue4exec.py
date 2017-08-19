'''
This is game engine. Main entry point when we launch the simulation in-game.
Import only this file from embedded C++/Python app. to simplify things.
'''


from simcubes.behaviours.basebehaviour import iter_threads_in_holders
from simcubes.simcore import cSimEnvironment

from levelgenerator.plain import generate_test_landscape

'''
Basic game engine interface
'''


def start_world_and_return_sim_environment(aworld):
    '''
    This is called from game engine. We hold a reference to the environment there and pass it every time
    we need to do something with the game.
    :param aworld: cWorld instance (from the level generator)
    :return: cSimEnvironment instance
    '''
    env = cSimEnvironment()
    for thr_i in iter_threads_in_holders(aworld.iter_over_blocks()):
        env.start_a_thread(thr_i)
    return env


def run_simulation_interval(env, timeunits):
    '''
    Advance simulation futher and return events that should be animated
    (at the moment, these are all happened events).
    :param env: cSimEnvironment instance
    :param timeunits: a float that describes simulation speed
    :return: a list of animated events
    '''
    sch = env.get_the_schedule()
    events_happend = sch.apply_delta_timeunits(timeunits)
    return events_happend


if __name__ == '__main__':
    T = 10
    dt = 0.1

    # this won't be called in game
    world = generate_test_landscape()
    env = start_world_and_return_sim_environment(world)

    for t in range(0, T):
        new_events = run_simulation_interval(env, dt)
        print("t={}  Events to animate {}".format(t, len(new_events)))



