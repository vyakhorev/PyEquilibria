
'''
Test the simulation calls
'''

# TODO: we need better tests, asyncio would be helpful

import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from misc import lg
    lg.config_logging()

    from levelgenerator.plain import generate_test_landscape
    from misc.exec import realtime_batch_simulation_cycle
    from ue4exec import start_world_and_return_sim_environment, run_simulation_interval

    # create simulation schedule
    # env = cSimEnvironment()
    # spawn a blooming grass plane
    level = generate_test_landscape()
    env = start_world_and_return_sim_environment(level)
    list_of_events = run_simulation_interval(env, 1)
    for ev_i in list_of_events:
        print(ev_i.get_parent_gid())


    # activate the threads in the environment
    # for thr_i in iter_threads_in_holders(level.iter_over_blocks()):
    #     env.start_a_thread(thr_i)
    # Start a simulation cycle with batch ticks
    # Two variants implemented:

    # realtime_batch_simulation_cycle(env, 10)
    # one_time_simulation(env, 4)
