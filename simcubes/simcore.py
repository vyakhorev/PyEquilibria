
from heapq import heappush, heappop
from itertools import count

import logging
logger = logging.getLogger(__name__)

class cSimEnvironment:
    '''
    Our environment consists of connected asyncronious threads (behaviours).
    This class manages these threads: iterates over them to gather simulation schedule,
    activates and deactives them.
    '''

    def __init__(self):
        self.threads = []  # used only for observing, the mechanics don't rely on this list yet
        self.schedule = cSimSchedule()

    def get_time(self):
        '''
        :return: simulation time
        '''
        return self.schedule.get_time()

    def get_the_schedule(self):
        '''
        Game engine gets the reference to the schedule from here
        and opererates directly with apply_next_tick method.
        :return: the cSimSchedule instance
        '''
        return self.schedule

    def start_a_thread(self, async_thread):
        '''
        Do the first step and schedule the first event.
        All the rest events would be scheduled with like
        a chain reaction.
        '''
        async_thread.set_environment(self)
        self.threads += [async_thread]  # this is not used in core mechanics
        async_thread.first_step()  # this would call cSimSchedule.schedule_event

    def start_threads(self, iter_over_threads):
        for thr_i in iter_over_threads:
            self.start_a_thread(thr_i)


class cSimSchedule:
    '''
    Activates the scheduled events in the correct order.
    Game Engine should synchronise it's ticks with this
    schedule.
    '''

    def __init__(self):
        self._heap = []  # a heap to hold the events
        self._recent_events = []  # these eventes just happened and not visible in the game yet
        self._now = 0.0

    def get_time(self):
        return self._now

    def peek_next_event(self):
        '''
        :return: a tuple (event_time, event_priority, event_reference)
        (unpack for destoying a reference to the actual schedule)
        '''
        T, P, an_event = self._heap[0]
        return T, P, an_event

    def peek_next_timestamp(self):
        return self._heap[0][0]

    def schedule_event(self, ev):
        '''
        Schedule an event with a
        :param ev: some event with known duration
        '''
        heappush(self._heap, (round(self._now + ev.duration, 5), ev.priority, ev))

    def apply_next_tick(self, until_T):
        '''
        Game engine should call this method frequently (each 0.1 seconds).
        This call 'reserves' all the events up to the moment until_T. They
        will be activated right at the moment of the call, however the game
        should synchronise them with graphical representation.
        :param until_T: simulation time, we reserve the events up to this moment.
        :return: a list with activated events (so that game engine can easily
                find all the corresponding cubes).

        ..warning:
            If some of the threads produce only zero duration events, this call
            may never end.

        ..note:
            Game engine is reponsible to INCREF and DECREF for events, they'll be
            garbage collected on the next tick, when we empty self._recent_events.

        ..note:
            Game engine should read the states from the blocks after this call,
            before the next call.
        '''

        # There can be a lot of additional things here - like events cancellations

        self._recent_events = []  # free the references
        while self.peek_next_timestamp() <= until_T:
            self._now, P, an_event = heappop(self._heap)
            #logger.info("Simulation time is incremented up to " + str(self._now))
            if not an_event.cancelled:
                # applies an event and schedules the next one
                # so after this process_step() call new events
                # are heappuched inside self._heap.
                an_event.process_step()
                self._recent_events += [an_event]
        # Progress time anyway
        self._now = max(self._now, until_T)

        return self._recent_events

    def apply_delta_timeunits(self, dt):
        return self.apply_next_tick(self._now+dt)

    def apply_event_after_event(self):
        '''
        Iterative call to apply events until forced to be stoped.
        '''
        while True:
            self._now, P, an_event = heappop(self._heap)
            #logger.info("Simulation time is incremented up to " + str(self._now))
            if not an_event.cancelled:
                an_event.process_step()
            yield self._now


class cAsyncThread:
    '''
    Event generator for environment, a process. May be active and
    inactive. In latter case there should be no events from this
    thread in the simulation.
    '''

    thread_count = count(0)

    def __init__(self):
        self.thread_id = next(self.thread_count)
        self.env = None  # to be set upon cSimEnvironment.start_a_thread
        self.do_schedule = None  # to be set upon cSimEnvironment.start_a_thread
        self.generator_state = None  # to be set after
        self.last_failed_event = None  # event that was right before the snooze call
        self.snoozed = False

    def __eq__(self, other):
        return self.thread_id == other.thread_id

    def __repr__(self):
        return "thread {}".format(self.thread_id)

    def __hash__(self):
        # this is not obligatory for simulation, but is utilised in animation
        return hash(self.thread_count)

    def get_time(self):
        '''
        :return: simulation time
        '''
        return self.env.get_time()

    def set_environment(self, env):
        self.env = env
        self.do_schedule = lambda ev: env.schedule.schedule_event(ev)

    def run(self):
        '''
        Write logic here, generate events in any order under any rules.
        Behaviours implement state-dependent activity with external
        switch calls from events.
        '''
        is_active = True
        while is_active:
            # yield any cEvent here, timeout is obligatory
            raise NotImplemented

    def first_step(self):
        '''
        Environment does the first step, events do the rest steps.
        '''
        self.generator_state = self.run()
        self.step()

    def step(self):
        '''
        A technical call to schedule the next event. First time it is called from the
        environment to schedule the first event. After that this is called
        from event upon finishig.
        '''
        if self.generator_state is None:
            # It's ok, run can generate no events
            return
        try:
            if self.snoozed:
                return

            # main generator loop here
            next_event = next(self.generator_state)
            self.do_schedule(next_event)

        except StopIteration:
            # it's ok, event generators can stop
            self.after_last_step()

    def snooze(self):
        '''
        This would stop this instance (see step). So the event would not schedule the next
        event.
        '''
        self.snoozed = True
        logger.info("[t={}][{} is snoozed]".format(self.get_time(),self))

    def wake(self):
        '''
        Resume stepping over the event generator. We should have a link to the last
        failed event. So that we can just reschedule it again, it would step in the end.
        '''
        if not self.snoozed:
            return
        self.snoozed = False
        if self.last_failed_event is None:
            # If the process just stoped without failure
            self.step()
            logger.info("[t={}][{} is activated with next event]".format(self.get_time(), self))
        else:
            self.do_schedule(self.last_failed_event)
            self.last_failed_event = None
            logger.info("[t={}][{} is activated last failed event]".format(self.get_time(), self))

    def after_last_step(self):
        '''
        Override this if you want to call something after the process ends
        '''
        pass

# Events

class cEvent:
    '''
    Base event class. Useful aslo as a timeout.
    All the priorities should be diffrent, depending on the
    event class. The lower the value, the higher is the priority.
    This sets execution order.
    '''

    priority = 10

    def __init__(self, beh, duration):
        self.beh = beh
        self.duration = duration
        # a way to cancel events (after block destruction for example)
        self.cancelled = False

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __repr__(self):
        return "EVENT {} planned by {}".format(self.__class__.__name__, self.beh)

    def get_time(self):
        return self.beh.get_time()

    def get_parent_gid(self):
        # UE4 call
        return self.beh.parent.gid

    def get_behaviour_role(self):
        # UE4 call, won't work on basic AsyncThread
        return self.beh.behaviour_role

    def process_step(self):
        '''
        This thing is call from the schedule to complete an event.
        Behaviour inherits cAsyncThread. It has a generator run()
        that produce events. As soon as this event is applied
        we should step further and schedule next event (afterwards,
        this event would be garbage collected and new event would
        do the same in it's turn.

        So the next event is scheduled right after the previous one
        is applied
        '''
        success = self.apply()
        if not success:
            logger.info("[t={}][{} - failed]".format(self.get_time(), self))
            self.beh.snooze()  # this would stop the behaviour generator
            self.rollback_in_case_of_failure()
            self.beh.last_failed_event = self
            return
        if self.__class__.__name__ != "cEvent":  # omit the timeouts
            logger.info("[t={}][{} - success]".format(self.get_time(), self))
        self.beh.step()

    def apply(self):
        '''
        Implement the event logic (over self.beh) here. You MUST return True or False.

        In case of a failure the 'thread' would be stopped, the event would
        be saved for a retry.
        :return: Return True in case of success. Return False in case of a failure.
        '''
        return True

    def rollback_in_case_of_failure(self):
        '''
        This would be called in case if apply returns False.
        So if apply logic changed some state before the failure, you can implement
        rollback operations here.
        '''
        pass