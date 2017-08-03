'''
Async. threads that record data points regulary.
Don't use it in game, this is testing purposes only.
'''

from misc.datatesting import cSimPeriodicObserver, cSimulationResultsContainer

def add_observers(simenv, period = 0.05):
    """
    Build an instance of cSimulationResultsContainer, setup observers.
    :param simenv: environment with activated threads we need to observe.
    :param period: how frequently should we log the data.
    :return: a cSimulationResultsContainer instance. Plus, it mutates simenv.
    """

    data_collector = cSimulationResultsContainer()

    new_obs = []
    for thr_i in simenv.threads:
        if hasattr(thr_i, "snoozed") and thr_i.__class__.__name__ != 'cBox':
            new_obs += [cSnoozeObserver(thr_i, data_collector, period)]
        if hasattr(thr_i, "storage"):
            new_obs += [cCargoObserver(thr_i, data_collector, period)]

    simenv.start_threads(new_obs)

    return data_collector


# Below are conrete observers for different cases

class cCargoObserver(cSimPeriodicObserver):
    def observe_data(self):
        # ts_name = "volume"
        # ts_value = self.target.storage.get_volume()
        # self.record_data(ts_name, ts_value)
        for item_type_i, level_i in self.target.storage.loop_over_levels():
            self.record_data('level of ' + str(item_type_i), level_i)

class cSnoozeObserver(cSimPeriodicObserver):
    def observe_data(self):
        ts_name = "is snoozed"
        ts_value = self.target.snoozed
        self.record_data(ts_name, ts_value)

