'''
This is UE4 interface
'''

from levelgenerator.plain import generate_test_landscape
from simcubes.simcore import cSimEnvironment
from simcubes.behaviours.basebehaviour import iter_threads_in_holders

def start_world_and_return_sim_environment(aworld):
    env = cSimEnvironment()
    for thr_i in iter_threads_in_holders(aworld.iter_over_blocks()):
        env.start_a_thread(thr_i)
    return env

def run_simulation_interval(env, timeunits):
    sch = env.get_the_schedule()
    events_happend = sch.apply_delta_timeunits(timeunits)
    return events_happend
