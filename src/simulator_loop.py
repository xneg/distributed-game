import time
import logging

from consistency_checker import ConsistencyChecker
from singleton import Singleton
from timer import Timer


def _has_method(o, name):
    return callable(getattr(o, name, None))


class SimulatorLoop(metaclass=Singleton):
    def __init__(self, objects=None, sleep_interval=1.0):
        self._objects = objects
        self._sleep_interval = sleep_interval

    def add_object(self, obj):
        self._objects.append(obj)

    def loop(self):
        while True:
            Timer().process()

            for o in self._objects.copy():
                o.process()
                if _has_method(o, "destroyed") and o.destroyed():
                    self._objects.remove(o)

            ConsistencyChecker().process()

            time.sleep(self._sleep_interval)
            logging.debug(f"Total objects count {len(self._objects)}")
