from constant_object import ConstantObject


class Timer(ConstantObject):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Timer, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._epoch = 0

    def current_epoch(self):
        return self._epoch

    def process(self):
        self._epoch = self._epoch + 1