
from simcubes.simcore import cAsyncThread, cEvent
from simcubes.en import ItemTypes, resource_volumes

import random

import logging
logger = logging.getLogger(__name__)


class cItemStorage:
    '''
    Define storage methods here: put, get + dict with items
    '''
    def __init__(self, max_volume=0, owner=None):
        '''
        :param max_volume: set 0 for infinite
        '''
        self._piles = {}
        self.max_volume = max_volume
        self._volume = 0
        self.owner = owner
        # A storage can become full and no-more-full.
        # A pile can become empty and no-more-empty.
        # A pile calls a method of cItemStorage to
        # wake up connected threads.
        self.callback_on_no_more_empty = None
        self.callback_on_no_more_full = None
        self.IS_FULL = False
        # self.IS_EMPTY = True

    def __repr__(self):
        return 'cItemStorage for {}'.format(self.owner)

    def set_callback_on_no_more_empty(self, callback):
        '''
        Event when this storage starts to be non-empty after being empty 
        '''
        self.callback_on_no_more_empty = callback

    def set_callback_on_no_more_full(self, callback):
        '''
        Event when this storage starts to be not full after being full
        '''
        self.callback_on_no_more_full = callback

    def call_callback_no_more_full(self):
        '''
        Do the callback itself.
        '''
        logger.info('{} no_more_full'.format(self))
        if not(self.callback_on_no_more_full is None):
            self.callback_on_no_more_full()

    def call_callback_no_more_empty(self):
        '''
        Do the callback itself.
        '''
        logger.info('{} no more empty'.format(self))
        if not(self.callback_on_no_more_empty is None):
            self.callback_on_no_more_empty()

    def loop_over_levels(self):
        for res_type, pile_i in self._piles.items():
            yield res_type, pile_i.get_level()

    def get_volume(self):
        return self._volume

    def _get_pile(self, item_type):
        if not(item_type in self._piles):
            pile = cItemPile(resource_volumes[item_type])
            self._piles[item_type] = pile
        else:
            pile = self._piles[item_type]
        return pile

    def take_one_random(self):
        #FIXME: fix this bad code
        non_empty = []
        for kv in filter(lambda kv: kv[1].get_level() > 0, self._piles.items()):
            non_empty += [kv]

        if len(non_empty) == 0:
            return -1, 0

        res_type_i, pile_i = random.choice(non_empty)
        qtty_to_take = 1
        self.take(res_type_i, qtty_to_take)

        return res_type_i, qtty_to_take

    def put(self, item_type, quantity):
        pile = self._get_pile(item_type)
        if self.max_volume != 0:  # infinite volume
            if self._volume + pile.estimate_volume(quantity) > self.max_volume:
                self.IS_FULL = True
                return False
        pile.put(quantity)  # always possible
        self._volume += pile.estimate_volume(quantity)
        if pile.IS_EMPTY:
            pile.IS_EMPTY = False
            self.call_callback_no_more_empty()
        return True

    def take(self, item_type, quantity):
        pile = self._get_pile(item_type)
        if pile.take(quantity):
            self._volume -= pile.estimate_volume(quantity)
            if self.IS_FULL:
                self.IS_FULL = False
                self.call_callback_no_more_full()
            return True
        else:
            pile.IS_EMPTY = True
            return False

    def check_package_availability(self, package):
        for item, qtty in package:
            if not (item in self._piles):
                return False
            if self._piles[item].get_level() < qtty:
                return False
        return True

    def check_package_for_available_space(self, package):
        sum_space = 0
        for item, qtty in package:
            sum_space += resource_volumes[item] * qtty

        if sum_space <= self.max_volume - self._volume:
            return True

        return False

    def take_package(self, package):
        """
        :param package: list of tuples [(someItem, 1),(someItem2, 3)]
        :return: Boolean
        """
        package_ready = True

        if not self.check_package_availability(package):
            package_ready = False

        if package_ready:
            for item, qtty in package:
                self.take(item, qtty)

        return package_ready


class cItemPile:
    '''
    A pile of single-type of items
    '''

    def __init__(self, volume_per_unit, init_quantity=0):
        self.quantity_of_units = init_quantity  # Try to keep it integer
        self.volume_per_unit = volume_per_unit
        # This attribute is modified from storage since
        # it's better to leave the context and backups
        # there (we are volume limited within a storage).
        self.IS_EMPTY = True

    def get_volume(self):
        return self.estimate_volume(self.quantity_of_units)

    def get_level(self):
        return self.quantity_of_units

    def estimate_volume(self, quantity):
        return quantity * self.volume_per_unit

    def put(self, quantity):
        self.quantity_of_units += quantity

    def take(self, quantity):
        if self.quantity_of_units - quantity < 0:
            return False
        self.quantity_of_units -= quantity
        return True


class cBox(cAsyncThread):
    def __init__(self, name='default', max_volume=0):
        super().__init__()
        self.name = name

        self.pullers = []
        self.pushers = []

        self.storage = cItemStorage(max_volume, owner=self)
        self.storage.set_callback_on_no_more_empty(lambda: self.on_no_more_empty())
        self.storage.set_callback_on_no_more_full(lambda: self.on_no_more_full())

    def __repr__(self):
        return self.name + " " + super().__repr__()

    def add_puller(self, thr):
        self.pullers += [thr]

    def add_pusher(self, thr):
        self.pushers += [thr]

    def on_no_more_empty(self):
        for thr_i in self.pullers:
            thr_i.wake()

    def on_no_more_full(self):
        for thr_i in self.pushers:
            thr_i.wake()


    def run(self):
        pass


class cFarm(cAsyncThread):
    def __init__(self, item_type, name='default', max_volume=0, yield_per_period=1, period=1.0):
        super().__init__()
        self.name = name
        self.item_type = item_type
        self.yield_per_period = yield_per_period
        self.period = period

        self.pullers = []

        self.storage = cItemStorage(max_volume, owner=self)
        self.storage.set_callback_on_no_more_empty(lambda: self.on_no_more_empty())
        self.storage.set_callback_on_no_more_full(lambda: self.on_no_more_full())

    def __repr__(self):
        return self.name + " " + super().__repr__()

    def add_puller(self, thr):
        self.pullers += [thr]

    def on_no_more_empty(self):
        for thr_i in self.pullers:
            thr_i.wake()

    def on_no_more_full(self):
        self.wake()

    def run(self):
        while True:
            yield cSpawnItem(thr=self,
                             duration=self.period,
                             storage=self.storage,
                             item_type=self.item_type,
                             quantity=self.yield_per_period)


class cConveyor(cAsyncThread):
    def __init__(self, name='default', period=1.0):
        super().__init__()
        self.name = name
        self.period = period
        # Setup storage behaviour
        self.source = None
        self.sink = None
        self.storage = cItemStorage(max_volume=0, owner=self)  #TODO: need a simplified storage for conveyors
        self.storage.set_callback_on_no_more_empty(lambda: self.on_no_more_empty())
        self.storage.set_callback_on_no_more_full(lambda: self.on_no_more_full())

    def __repr__(self):
        return self.name + " " + super().__repr__()

    def set_source(self, thr):
        self.source = thr

    def set_sink(self, thr):
        self.sink = thr

    def on_no_more_empty(self):
        if not(self.source is None):
            self.source.wake()

    def on_no_more_full(self):
        if not(self.sink is None):
            self.sink.wake()

    def run(self):
        while True:
            if self.source is None or self.sink is None:
                self.snooze()
                return

            # need to be clean-uped
            yield cEventPullPushOneRandomItem(thr=self,
                                              duration=self.period,
                                              source_storage=self.source.storage,
                                              sink_storage=self.storage)

            yield cEventPullPushOneRandomItem(thr=self,
                                              duration=self.period,
                                              source_storage=self.storage,
                                              sink_storage=self.sink.storage)


class cCrafter(cAsyncThread):
    def __init__(self, name='default', max_volume=0, period=1.0):
        super().__init__()
        self.name = name
        self.period = period

        self.source = None
        self.sink = None
        self.connected = []

        self.storage = cItemStorage(max_volume=max_volume, owner=self)
        self.storage.set_callback_on_no_more_empty(lambda: self.on_no_more_empty())
        self.storage.set_callback_on_no_more_full(lambda: self.on_no_more_full())

        # todo make recipe's class
        self.recipe = (ItemTypes.itBread, [(ItemTypes.itWheat, 1), (ItemTypes.itWater, 1)])

    def __repr__(self):
        return self.name + " " + super().__repr__()

    def set_source(self, thr):
        self.source = thr
        self.connected += [thr]

    def set_sink(self, thr):
        self.sink = thr
        self.connected += [thr]

    def on_no_more_empty(self):
        self.wake()  # excessive since we craft directly from the source
        for thr_i in self.connected:
            # we can optimise this with waking up only sources
            thr_i.wake()

    def on_no_more_full(self):
        self.wake()
        for thr_i in self.connected:
            # we can optimise this with waking up only sinks
            thr_i.wake()

    def run(self):
        while True:
            if self.source is None: # or self.sink is None:
                self.snooze()
                return

            yield cEventApplyRecipe(thr=self,
                                    duration=self.period,
                                    source_storage=self.source.storage,
                                    sink_storage=self.storage,
                                    recipe=self.recipe)


# class cRecipe:
#     '''
#     Represents a schema that can be applied within a crafter box
#     '''
#     def __init__(self):
#         self.sources =


class cEventPullPushOneRandomItem(cEvent):

    priority = 1

    def __init__(self, thr, duration, source_storage, sink_storage):
        super().__init__(thr, duration)
        self.source_storage = source_storage
        self.sink_storage = sink_storage

    def apply(self):
        item_type, quantity = self.source_storage.take_one_random()

        if item_type == -1:
            return False

        is_balanced = self.sink_storage.put(item_type, quantity)

        if not is_balanced:
            # rollback!
            self.source_storage.put(item_type, quantity)
            return False
        
        return True


class cEventApplyRecipe(cEvent):
    priority = 1

    def __init__(self, thr, duration, source_storage, sink_storage, recipe):
        super().__init__(thr, duration)
        self.source_storage = source_storage
        self.sink_storage = sink_storage
        self.recipe = recipe
        # self.item_type = item_type
        # self.quantity = quantity

    def apply(self):
        if self.sink_storage.check_package_for_available_space(self.recipe[0]) and \
        self.source_storage.check_package_availability(self.recipe[1]):

            a = self.source_storage.take_package(self.recipe[1])
            b = self.sink_storage.put(self.recipe[0], 1)

            return True

        return False


class cSpawnItem(cEvent):

    priority = 1

    def __init__(self, thr, duration, storage, item_type, quantity):
        super().__init__(thr, duration)
        self.storage = storage
        self.item_type = item_type
        self.quantity = quantity

    def apply(self):
        if self.storage.put(self.item_type, self.quantity):
            return True
        return False


if __name__ == '__main__':
    from misc import lg
    lg.config_logging()

    from simcubes.simcore import cSimEnvironment
    from misc.exec import one_time_simulation
    from misc.observers import add_observers

    env = cSimEnvironment()

    # Creating entities
    box1 = cBox(name='BOX buffer', max_volume=50)
    box2 = cBox(name='BOX final', max_volume=50)

    farm1 = cFarm(name='FARM of wheat', item_type=ItemTypes.itWheat, max_volume=25, period=0.1)
    farm2 = cFarm(name='FARM of water', item_type=ItemTypes.itWater, max_volume=25, period=0.05)

    conv1 = cConveyor(name='CONVEYOR from wheat farm to buffer box', period=0.5)
    conv2 = cConveyor(name='CONVEYOR from water farm to buffer box', period=0.5)
    conv3 = cConveyor(name='CONVEYOR from bakery to final box', period=15)

    crafter_in_box1 = cCrafter(name='CRAFTER bakery connected to buffer box', max_volume=15)

    conv1.set_source(farm1)
    farm1.add_puller(conv1)

    conv2.set_source(farm2)
    farm2.add_puller(conv2)

    box1.add_pusher(conv1)
    box1.add_pusher(conv2)
    conv1.set_sink(box1)
    conv2.set_sink(box1)

    crafter_in_box1.set_source(box1)
    box1.add_puller(crafter_in_box1)

    crafter_in_box1.set_sink(conv3)
    conv3.set_source(crafter_in_box1)

    conv3.set_sink(box2)
    box2.add_puller(conv3)

    # schedule first events
    env.start_threads([farm1, farm2, conv1, conv2, box1, crafter_in_box1, box2, conv3])

    data_collector = add_observers(env, period=0.01)

    one_time_simulation(env, 100)

    saveto = '..//..//__temp//test.pdf'
    data_collector.save_plots(saveto)

