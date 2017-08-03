'''
Execution utilities, useful for testing and textual-kind of game.
'''

import time
import logging
logger = logging.getLogger(__name__)

def realtime_batch_simulation_cycle(env, seconds, tick_seconds=1, factor = 10, dolog=True):
    '''
    Starts realtime simulation of a given environment
    :param env: cSimEnvironment, a storage for schedule and an
                'entry point' for all the behaviours.
    :param seconds: simulation will last this time
    :param tick_seconds: how frequent are the ticks
    :param factor: multiply game time for this number to get:
            factor * gametime = 1 real second. The smaller the
            factor, the faster is the 'game'.
    '''
    game_time = 0
    t = 0
    sch = env.get_the_schedule()

    while t <= seconds:
        start_time = time.monotonic()
        # sleeping for dt between events would be much more accurate.
        game_time += tick_seconds/factor
        time.sleep(tick_seconds)
        t+= tick_seconds
        events_happend = sch.apply_next_tick(game_time)
        events_count = str(len(events_happend))
        real_dt = str(time.monotonic() - start_time)
        if dolog:
            logger.info('game time is ' + str(game_time) + ', real tick is ' + real_dt + ',  events happened: ' + events_count)

def one_time_simulation(env, until):
    '''
    Does a single run for the environment
    :param env: cSimEnvironment, a storage for schedule
    :param until: simulate until this gametime
    '''

    sch = env.get_the_schedule()

    for t in sch.apply_event_after_event():
        if t > until:
            break

