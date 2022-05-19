import time

from engine.singleton import Singleton


def _has_method(o, name):
    return callable(getattr(o, name, None))


class SimulatorLoop(metaclass=Singleton):
    def __init__(
        self, timer=None, consistency_checker=None, objects=None, sleep_interval=1.0
    ):
        self._timer = timer
        self._consistency_checker = consistency_checker
        self._objects = objects if objects else []
        self._sleep_interval = sleep_interval

    def add_object(self, obj):
        self._objects.append(obj)

    def loop(self):
        while True:
            self.process()

            if self._sleep_interval > 0:
                time.sleep(self._sleep_interval)

    def process(self):
        if self._timer:
            self._timer.process()

        for o in self._objects.copy():
            o.process()
            if _has_method(o, "destroyed") and o.destroyed():
                self._objects.remove(o)

        if self._consistency_checker:
            self._consistency_checker.process()

    @property
    def objects(self):
        return self._objects
