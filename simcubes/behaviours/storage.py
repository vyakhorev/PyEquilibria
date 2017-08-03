'''
Different aspects of storage and delivery
'''


import logging

from simcubes.behaviours.basebehaviour import cSimulBehaviour
from simcubes.simcore import cEvent

logger = logging.getLogger(__name__)


class cBehItemStorage(cSimulBehaviour):

    def __init__(self, parent):
        super().__init__(parent)
        self.quantity = 0
        self.max_quantity = 50
        self.pullers = []
        self.pushers = []

    def connect_to(self, other_behaviour, puller=False, pusher=False):
        super().connect_to(other_behaviour)
        if puller:
            self.pullers += [other_behaviour]
        if pusher:
            self.pushers += [other_behaviour]

    def disconnect_from(self, other_behaviour):
        super().disconnect_from(other_behaviour)
        if isinstance(other_behaviour, cBehItemPullPush):

            try:
                i = self.pullers.index(other_behaviour)
                self.pullers.pop(i)
            except ValueError:
                # it's ok
                pass

            try:
                i = self.pushers.index(other_behaviour)
                self.pushers.pop(i)
            except ValueError:
                # it's ok
                pass

    def run(self):
        pass

    def put(self, quantity):

        if self.quantity + quantity > self.max_quantity:
            return False

        # The storage changes it's state to "have something"
        if self.quantity == 0 and quantity > 0:
            for p in self.pullers:
                p.get_poked()

        self.quantity += quantity
        return True

    def take(self, quantity):

        if self.quantity - quantity < 0:
            return False

        for p in self.pushers:
            p.get_poked()

        self.quantity -=quantity
        return True

    def get_poked(self):
        pass


class cBehSpawn(cSimulBehaviour):

    def __init__(self, parent):
        super().__init__(parent)
        self.quantity = 0
        self.per_period = 1
        self.period = 0.5
        self.max_quantity = 10
        self.pullers = []

    def connect_to(self, other_behaviour, puller=False):
        super().connect_to(other_behaviour)
        if puller:
            self.pullers += [other_behaviour]

    def disconnect_from(self, other_behaviour):
        super().disconnect_from(other_behaviour)
        if isinstance(other_behaviour, cBehItemPullPush):
            try:
                i = self.pullers.index(other_behaviour)
                self.pullers.pop(i)
            except ValueError:
                # it's ok
                pass

    def run(self):
        while True:
            yield cEventSpawnItem(self, self.period, self, self.per_period)

    def put(self, quantity):

        if self.quantity + quantity > self.max_quantity:
            return False

        # The storage changes it's state to "have something"
        if self.quantity == 0 and quantity > 0:
            for p in self.pullers:
                p.get_poked()

        self.quantity += quantity
        return True

    def take(self, quantity):

        self.get_poked()

        if self.quantity - quantity < 0:
            return False

        self.quantity -=quantity
        return True


class cBehPullItem(cSimulBehaviour):

    def __init__(self, parent):
        super().__init__(parent)
        self.quantity = 0
        self.max_quantity = 2
        self.period = 1
        self.per_period = 1
        self.source = None
        self.sink = None

    def connect_to(self, other_behaviour, source=False, sink=False):
        super().connect_to(other_behaviour)
        if source:
            self.source = other_behaviour
        if sink:
            self.sink = other_behaviour

    def run(self):
        while True:
            yield cEventPullItem(self, self.period, self.source, self.per_period)

    def put(self, quantity):
        self.get_poked()
        if self.quantity + quantity > self.max_quantity:
            return False

        if self.quantity == 0 and quantity > 0:
            if not self.sink is None:
                self.sink.get_poked()

        self.quantity += quantity
        return True

    def take(self, quantity):
        self.get_poked()
        if self.quantity - quantity < 0:
            return False

        if not self.source is None:
            self.source.get_poked()

        self.quantity -=quantity
        return True


class cBehPushItem(cSimulBehaviour):

    def __init__(self, parent):
        super().__init__(parent)
        self.quantity = 0
        self.max_quantity = 2
        self.period = 1
        self.per_period = 1
        self.source = None
        self.sink = None

    def connect_to(self, other_behaviour, source=False, sink=False):
        super().connect_to(other_behaviour)
        if source:
            self.source = other_behaviour
        if sink:
            self.sink = other_behaviour

    def run(self):
        while True:
            yield cEventPushItem(self, self.period, self.sink, self.per_period)

    def put(self, quantity):

        self.get_poked()

        if self.quantity + quantity > self.max_quantity:
            return False

        if self.quantity == 0 and quantity > 0:
            if not self.sink is None:
                self.sink.get_poked()

        self.quantity += quantity
        return True

    def take(self, quantity):

        self.get_poked()

        if self.quantity - quantity < 0:
            return False

        if not self.source is None:
            self.source.get_poked()

        self.quantity -= quantity
        return True

# don't use it
class cBehItemPullPush(cSimulBehaviour):

    def __init__(self, parent):
        super().__init__(parent)
        self.quantity = 0
        self.max_quantity = 5
        self.period = 0.2
        self.per_period = 1
        self.source = None
        self.sink = None

    def connect_to(self, other_behaviour, source=False, sink=False):
        super().connect_to(other_behaviour)
        if source:
            self.source = other_behaviour
        if sink:
            self.sink = other_behaviour

    def run(self):
        while True:
            success = yield cEventPullItem(self, self.period, self.source, self.per_period)
            success = yield cEventPushItem(self, self.period, self.sink, self.per_period)

    def put(self, quantity):
        if self.quantity + quantity > self.max_quantity:
            return False

        if self.quantity == 0 and quantity > 0:
            if not self.sink is None:
                self.sink.get_poked()

        self.quantity += quantity
        return True

    def take(self, quantity):
        if self.quantity - quantity < 0:
            return False

        if self.quantity == 0 and quantity > 0:
            if not self.sink is None:
                self.sink.get_poked()

        self.quantity -=quantity
        return True

###
# Events
###

class cEventSpawnItem(cEvent):

    priority = 1

    def __init__(self, beh, duration, target, quantity):
        super().__init__(beh, duration)
        self.target = target  # usually the same as behaviour
        self.quantity = quantity

    def apply(self):
        if self.target is None:
            return False
        is_spawned = self.target.put(self.quantity)
        return is_spawned


class cEventPullItem(cEvent):

    priority = 3

    def __init__(self, beh, duration, source, quantity):
        super().__init__(beh, duration)
        self.source = source
        self.quantity = quantity

    def apply(self):
        if self.source is None:
            return False
        is_pulled = self.source.take(self.quantity)
        if not is_pulled:
            return False
        is_balanced = self.beh.put(self.quantity)
        if not is_balanced:
            # logger.warning("Pull failed to balance")
            self.source.put(self.quantity)  # rollback
            return False
        return True


class cEventPushItem(cEvent):

    priority = 2

    def __init__(self, beh, duration, sink, quantity):
        super().__init__(beh, duration)
        self.sink = sink
        self.quantity = quantity

    def apply(self):
        if self.sink is None:
            return False
        is_taken = self.beh.take(self.quantity)
        if not is_taken:
            return False
        is_pushed = self.sink.put(self.quantity)
        if not is_pushed:
            logger.warning("Push failed to balance")
            self.beh.put(self.quantity)  # rollback
            return False
        return True


if __name__ == '__main__':
    from misc import lg
    lg.config_logging()

    from simcubes.simcore import cSimEnvironment
    from misc.exec import realtime_batch_simulation_cycle, one_time_simulation
    from misc.observers import add_observers

    env = cSimEnvironment()

    farm = cBehSpawn("FARM")
    pull1 = cBehPullItem("PULLER 1")
    push1 = cBehPushItem("PUSHER 1")
    # pull2 = cBehPullItem("PULLER 2")
    push2 = cBehPushItem("PUSHER 2")
    box1 = cBehItemStorage("BOX 1")
    # box2 = cBehItemStorage("BOX 2")
    # conv1 = cBehItemPullPush("CONV 1")
    # conv2 = cBehItemPullPush("CONV 2")
    # conv3 = cBehItemPullPush("CONV 3")
    # conv4 = cBehItemPullPush("CONV 4")
    # conv5 = cBehItemPullPush("CONV 5")
    # conv6 = cBehItemPullPush("CONV 6")

    # From farm to box 1
    farm.connect_to(pull1, puller=True)
    pull1.connect_to(farm, source=True)

    pull1.connect_to(push1, sink=True)
    push1.connect_to(pull1, source=True)

    # Conveyour to conveyour connects differentely, pushes directly
    push1.connect_to(push2, sink=True)
    push2.connect_to(push1, source=True)

    push2.connect_to(box1, sink=True)
    box1.connect_to(push2, pusher=True)

    # conv1.connect_to(conv2, sink=True)
    # conv2.connect_to(conv1, source=True)
    #
    # conv2.connect_to(box1, sink=True)
    # box1.connect_to(conv2, pusher=True)

    # From first conveyour to the next one
    # conv1.connect_to(conv2, source=False, sink=True)
    # conv2.connect_to(conv1, source=True, sink=False)

    env.start_threads([farm, pull1, push1, push2, box1])

    # Add periodically observing threads
    data_collector = add_observers(env, period=0.01)

    #realtime_batch_simulation_cycle(env, 15, tick_seconds=0.2, dolog=False)
    one_time_simulation(env, 25)

    data_collector.do_plot()

