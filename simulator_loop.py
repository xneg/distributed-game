import time

from singleton import Singleton
from timer import Timer


class SimulatorLoop(metaclass=Singleton):
    def __init__(self, objects):
        self._objects = []
        self._objects.append(Timer())
        self._objects.extend(objects)

    def add_object(self, obj):
        self._objects.append(obj)

    def loop(self):
        while True:
            # obj_copy = *self._objects
            for o in self._objects:
                if o.prepared():
                    o.process()

            self._objects = [o for o in self._objects if not o.destroyed()]

            time.sleep(1)
