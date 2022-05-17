import random
from functools import partial

from engine.simulator_loop import SimulatorLoop


class Signal:
    max_duration = 10

    def __init__(self, recipient, message, duration):
        self._duration = duration
        self._timer = 0
        self._destroyed = False
        self._send_message = partial(self.__send_message, recipient, message)

        SimulatorLoop().add_object(self)

    def process(self):
        self._timer = self._timer + 1

        if self._timer == self._duration:
            self._send_message()
            self._destroyed = True

    def destroyed(self):
        return self._destroyed

    @staticmethod
    def __send_message(recipient, message):
        recipient.add_message(message)


class SignalFactory:
    const_time = None
    max_duration = 10

    @staticmethod
    def create_signal(sender, recipient, message):
        duration = (
            SignalFactory.const_time
            if SignalFactory.const_time
            else random.randrange(1, SignalFactory.max_duration + 1)
        )
        Signal(recipient=recipient, message=message, duration=duration)
