import random

from simulator_loop import SimulatorLoop


class Link:
    def __init__(self, sender, recipient, message, const_time=None):
        self._duration = const_time if const_time else random.randrange(10)
        self._timer = 0
        self._prepared = False
        self._destroyed = False
        # TODO: try to use callback (currying)
        self._sender = sender
        self._recipient = recipient
        self._message = message

        SimulatorLoop().add_object(self)

    def prepared(self):
        if not self._prepared:
            self._prepared = True
            return False
        return True

    def process(self):
        if self._timer == self._duration:
            self._recipient.add_message(self._sender, self._message)
            self._destroyed = True

        self._timer = self._timer + 1

    def destroyed(self):
        return self._destroyed

    # def __send_message(self, recipient, message):
    #     recipient.add_message(message)
