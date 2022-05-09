from singleton import Singleton


class Timer(metaclass=Singleton):
    def __init__(self):
        self._epoch = 0

    def current_epoch(self):
        return self._epoch

    def process(self):
        self._epoch = self._epoch + 1