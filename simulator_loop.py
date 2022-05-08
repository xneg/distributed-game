import time

from timer import Timer


class Singleton (type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SimulatorLoop(metaclass=Singleton):
    def __init__(self, load_balancer, clients):
        self._objects = []
        self._objects.append(Timer())
        self._objects.append(load_balancer)
        self._objects.extend(clients)

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
