

# This is a third test with git - now console in action!
# Added something to check status

# Added something for console_branch

from simcubes.behaviours.basebehaviour import iter_threads_in_holders
from simcubes.simcore import cSimEnvironment

from levelgenerator.plain import generate_test_landscape

class cSimulationController:
    '''
    Receives commands and executes them. This is how one should manage the simulation.
    There are two types of commands:
    1) Ones that are executed before the simulation tick (commands to place a block for example)
    2) Ones that are executed right after the simulation tick (all types of queries)

    This class can help a lot to optimise screen-updates and to ensure coherent
    interactivity.

    The animation data (states of the cubes and other behaviour holders) is formed not in
    the game thread to optimise performance, that's why this thing with "requests" needed.

    ! Most of this class methods are UE4 calls !

    How to use:

    1) generate_world()   (need to add something smarter than that later)

    then every timer tick (or from tick to tick):
    2) (if needed)  schedule_update_animation_query()
    3) run_simulation_interval()
    4) (if needed)  iterate_over_animation_updates()
    '''

    def __init__(self):
        self.env = cSimEnvironment()  # cSimEnvironment instance
        self.world = None  # cSimWorld instance

        # Requests to process.
        # we have to ensure that if we receive multiple requests,
        # we'll reply once (to minimise the data sending). That's
        # why I have a set here.
        self.animation_updates_queries = set()

        # Another realisation that holds a reference to the callee
        # directly.
        self.animation_updates_queries_efficient = set()

        # Data to be sent to the game engine. Empty it every time
        # before the next timer tick - otherwise we may have old
        # data in game.
        self.animation_updates = {}

    ###
    # Animation updates (current state synchronisation)
    ###

    def next_animation_tick(self):
        '''
        Called when the client finally gets the data. Empty data here.
        We can't simply empty the data on run_simulation_interval since
        simulation can go a few ticks longer than it tooks to get the
        data (we get the data when we stop simulation, but we can do
        1-3 simulation ticks before getting data from it).
        '''
        self.animation_updates_queries = set()
        self.animation_updates_queries_efficient = set()  # may be inefficient )))
        self.animation_updates = {}

    def schedule_update_animation_query(self, entity_gid = None, role = None):
        '''
        Adds a request to send update information to the game engine.
        Will return information within a tick.
        :param entity_gid: gid of a cube or any other behaviour holder
                leave empty to query the whole active chunk.
        :param role: a code en.BehComponentRoles that encodes the component
                that's interested in the data. Leave empty to request
                all the available roles.
        '''
        self.animation_updates_queries.add((entity_gid, role))

    def schedule_update_animation_query_efficient(self, behaviour = None):
        '''
        A more efficient way of requesting an update about animation data.
        Excludes two look ups in dictionaries, can be called right from
        event. So if we have some recent events we can call
        a_controller.schedule_update_animation_query_efficient(ev.beh)
        to schedule animation update right after simulation tick.

        :param behaviour: A link to cSimulBehaviour, easy to get inside an event.
        '''
        self.animation_updates_queries_efficient.add(behaviour)

    def process_queries(self):
        '''
        Processes all the queries and stores them in self.animation_updates
        '''
        for beh_i in self.animation_updates_queries_efficient:
            self.animation_updates[(beh_i.parent.gid, beh_i.behaviour_role)] = beh_i.get_animation_data()

        for gid_i, role_i in self.animation_updates_queries:
            self.animation_updates[(beh_i.parent.gid, beh_i.behaviour_role)] = self.world.get_animation_data(gid_i, role_i)

    def iterate_over_animation_updates(self):
        '''
        After the client scheduled queries and called process_queries, it receives
        data from this call.
        :return: generator of gid, role, update_data to process animation updates.
        '''
        self.process_queries()
        for k, v in self.animation_updates.items():
            gid = k[0]
            role = k[1]
            update_data = v
            yield gid, role, update_data
        self.next_animation_tick()

    ###
    # Entity presense updates
    ###

    def iterate_over_blocks(self):
        '''
        Just an iterator over game blocks
        :return: generator of blocks
        '''
        # todo: active chunk only
        for bl_i in self.world.iter_over_blocks():
            yield bl_i

    ###
    # World generation
    ###

    def generate_world(self, schedule_updates=True):
        '''
        Generates the world and starts the asycnh threads in it.
        '''
        self.world = generate_test_landscape(15)
        for thr_i in iter_threads_in_holders(self.world.iter_over_blocks()):
            # this starts simulation
            self.env.start_a_thread(thr_i)
            # this will result in returning current states of all the cubes
        # Schedule initial updates so that we have actual data in game.
        # This is a temporary solution. A better solution would be to ask
        # for data explicitly.
        if schedule_updates:
            for thr_i in iter_threads_in_holders(self.world.iter_over_blocks()):
                self.schedule_update_animation_query_efficient(thr_i)


    def run_simulation_interval(self, timeunits, schedule_updates=True):
        '''
        Advance simulation futher and return events happened so that
        unreal engine can decide whether or not to transfer data
        about current state of each cube.
        :param env: cSimEnvironment instance
        :param timeunits: a float that describes simulation speed
        :param schedule_updates: shall plan to send update data to
                the game about each cube in the happened events.
        :return: a list of animated events
        '''
        # do the simulation tick
        sch = self.env.get_the_schedule()
        events_happend = sch.apply_delta_timeunits(timeunits)

        # greedy animation tactics: plan updates for all the events
        # (so that, UE4 shall receive all the updates). This is a
        # temporary solution, we can do better later.
        # this slows down simulation...
        if schedule_updates:
            for ev_i in events_happend:
                self.schedule_update_animation_query_efficient(ev_i.beh)

        return events_happend





