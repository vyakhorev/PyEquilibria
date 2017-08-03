
from simcubes.simcore import cAsyncThread

import logging
logger = logging.getLogger(__name__)


def iter_threads_in_holders(holders):
    '''
    Each cube have behaviours. In order to run them, we need to
    schedule them in the environment. This call heps us to do
    this.
    :param holders: a list of game world objects who inherit
    from cBehaviourHolder.
    '''
    for h_i in holders:
        for thr_i in h_i.iter_behaviours():
            yield thr_i


class cSimulBehaviour(cAsyncThread):
    '''
    Base class for simulation activities. A block can have multiple
    interacting behaviours. So block logic is reponsible only for
    connecting the behaviours with each other.

    When the behaviour is exposed to the world, one should think about
    it as a service. A service may need services of other types and
    provide services as well. As soon as the behaviour cannot provide
    it's service or it can't get the services from other behaviours,
    it becomes inactive (and becomes active when it's possible).
    '''

    def __init__(self, parent):
        '''
        :param parent: an object from the simulation (a block, a bunch of blocks).
                So parent is a subclass of cBehaviourHolder.
        '''
        super().__init__()
        self.parent = parent
        self.connected = []

    def __repr__(self):
        return "[behaviour of {}][{}]".format(self.parent, super().__repr__())

    def connect_to(self, other_behaviour):
        if not(other_behaviour in self.connected):
            self.connected += [other_behaviour]

    def disconnect_from(self, other_behaviour):
        '''
        This does not happen frequently, so it's ok to do some look ups here
        :param other_behaviour: disconnect from this behaviour
        '''
        try:
            i = self.connected.index(other_behaviour)
            self.connected.pop(i)
        except ValueError:
            logger.warning("An attempt to disconnect unrelated behaviour")

    def is_active(self):
        return not self.snoozed

    def get_poked(self):
        """
        This is called from other processes to wake up the thread.
        Default realisation - an attempt to wake up. There is no
        
        """
        self.wake()

    # to be deleted
    def check_activity_of_connections(self, service_type):
        '''
        Checks whether there is an active behaviour in the connection type
        pool. If all the connections are not active, it's a strong signal
        to suspend all the activity.
        :return: True if there is a single active connection. False otherwise.
        '''
        for _ in filter(lambda beh: beh.is_active(), self.connected[service_type]):
            return True

    # to be deleted
    def inform_connected_about_activation(self, service_type=None):
        '''
        When this behaviour starts to activate, it should inform all the
        clients about this fact so that they can decide whether to activate
        as well. Since the behaviour shouldn't take guesses who are the
        clients, we should inform everyone or at least some of them (by type).
        :param connection_type: (optional) inform only these types
        '''
        if service_type is None:
            for ser_type, beh in self.connected.items():
                beh.get_informed_about_activation(ser_type)
        else:
            for beh in self.connected[service_type]:
                beh.get_informed_about_activation(service_type)

    # to be deleted
    def inform_connected_about_deactivation(self, service_type=None):
        '''
        The opposite of inform_connected_about_activation
        :param connection_type: (optional) inform only these types
        '''
        if service_type is None:
            for ser_type, beh in self.connected.items():
                beh.get_informed_about_deactivation(ser_type)
        else:
            for beh in self.connected[service_type]:
                beh.get_informed_about_deactivation(service_type)

    # to be deleted
    def get_informed_about_activation(self, service_type):
        '''
        Implement this to optimise the simulation. If this behaviour
        needs this service type to be active in order to operate
        and there is no more connections of this type, it should
        suspend all the activity.

        In get_informed_about_deactivation we should stop the simulation,
        in get_informed_about_activation we should resume the simulation.

        :param service_type: this service type wants to inform you
                about activation. This is an external to this instance
                service type (if this is a conveyor, this would be "item
                provider").
        '''
        pass

    # to be deleted
    def get_informed_about_deactivation(self, service_type):
        '''
        Implement this to optimise the simulation. You should deactivate
        the simulation 'service' if you rely on this service type and
        there is no more active providers.
        This is the opposite of get_informed_about_activation.

        :param service_type: this service type wants to inform you
                about activation. This is an external to this instance
                service type (if this is a conveyor, this would be "item
                provider").
        '''
        pass


class cBehaviourHolder:
    '''
    Base class for all simulation blocks and aggregated instances.
    Holds all the behaviours, exposes their variables and states
    as a single callee.

    С++ code doesn't know about behaviours. but it can read the
    variables from here. Oh maybe this is not a good idea..
    '''

    def __init__(self):
        self.unique_behaviours = []
        self.behaviours = {}  # by service type, with duplicated references

    def iter_behaviours(self):
        for beh in self.unique_behaviours:
            yield beh

    def register_behaviour(self, behaviour, service_type = 0):
        '''
        Adds a behaviour into this entity (which is supposed to be
        either a block or a chunk).
        :param behaviour: new internal behaviour
        :param service_type: this is how this behaviour is exposed
                to the world. Based on this the cube's behaviour
                would be automatically connected to another cube.
                0 is for internal (not exposed) behaviours.
        '''
        # add to the plain list (may be multiple calls for different
        # service types).
        if not(behaviour in self.unique_behaviours):
            self.unique_behaviours += [behaviour]
        # register as a service
        if not(service_type in self.behaviours):
            self.behaviours[service_type] = []
        if not(behaviour in self.behaviours[service_type]):
            self.behaviours[service_type] += [behaviour]
        else:
            # duplicates in one service type are not expected
            logger.error('Attempt to add a duplicating behaviour for one service type!')
            raise BaseException('Attempt to add a duplicating behaviour for one service type')

    def handler_to_service_type(self, service_type):
        '''
        Use this to get the list of services by the service_type

        :param service_type: en.ServiceTypes
        :return: a reference to the corresponding list
        '''
        if service_type in self.behaviours:
            return self.behaviours[service_type]
        else:
            logger.error('Attempt to get a non-existing service type!')
            raise BaseException('Attempt to get a non-existing service type')

    def connect_to_another_holder(self, other_holder, inner_service_type=None, external_service_type=None):
        '''
        The main entry point for behaviour connection of one behaviour holder with another.
        For example, this is called when cubes find a match with service layers.

        Override this call in order to change or improve connection routine!

        :param other_holder: the other behaviour holder.
        :param inner_service_type: service type from this entity
        :param external_service_type: service type of other entity
        '''
        if not(inner_service_type is None or external_service_type is None):
            self.behavioural_connect_to(other_holder, inner_service_type, external_service_type)

    def behavioural_connect_to(self, other_holder, inner_service_type, external_service_type):
        '''
        This may simplify connection of one block to another.

        Connect to another behaviour holder (a block or a chunk usually).
        Shall take all the behaviours from other_holder with external_service_type
        and connect them with all the behaviours from this entity with inner_service_type.
        Usually this is a 1-to-1 connection.

        Each concrete realisation should decide for it's own whether it
        wants to connect to another block or not.

        :param other_holder: the other behaviour holder.
        :param inner_service_type: service type from this entity
        :param external_service_type: service type of other entity
        '''
        for beh_internal in self.handler_to_service_type(inner_service_type):
            for beh_external in other_holder.handler_to_service_type(external_service_type):
                # example:
                # beh_internal - a box behaviour of this block
                # beh_external - a conveyor behaviour from another block
                # inner_service_type - "item provider"
                # external_service_type - "item puller"
                beh_internal.connect_to(beh_external, inner_service_type)
                beh_external.connect_to(beh_internal, external_service_type)
