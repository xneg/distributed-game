import random
from functools import partial

from simulator_loop import SimulatorLoop


class Link:
    max_duration = 10

    def __init__(self, sender, recipient, message, const_time=None):
        self._duration = const_time if const_time else random.randrange(Link.max_duration)
        self._timer = 0
        self._destroyed = False
        self._send_message = partial(self.__send_message, sender, recipient, message)

        SimulatorLoop().add_object(self)

    def process(self):
        if self._timer == self._duration:
            self._send_message()
            self._destroyed = True

        self._timer = self._timer + 1

    def destroyed(self):
        return self._destroyed

    @staticmethod
    def __send_message(sender, recipient, message):
        recipient.add_message(sender, message)
