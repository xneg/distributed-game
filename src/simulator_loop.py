import time

from consistency_checker import ConsistencyChecker
from singleton import Singleton
from timer import Timer


def _has_method(o, name):
    return callable(getattr(o, name, None))


class SimulatorLoop(metaclass=Singleton):
    def __init__(self, objects, sleep_interval=1.0):
        self._objects = objects
        self._sleep_interval = sleep_interval

    def add_object(self, obj):
        self._objects.append(obj)

    def loop(self):
        while True:
            # obj_copy = *self._objects
            Timer().process()
            for o in self._objects:
                if not _has_method(o, "prepared") or o.prepared():
                    o.process()

            ConsistencyChecker().process()

            self._objects = [
                o
                for o in self._objects
                if not _has_method(o, "destroyed") or not o.destroyed()
            ]

            time.sleep(self._sleep_interval)
