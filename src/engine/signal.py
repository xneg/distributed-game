import random
from functools import partial
from uuid import UUID

from engine.contracts import MessagePacket, MessageResponse
from engine.simulator_loop import SimulatorLoop


class Signal:
    max_duration = 10

    def __init__(self, recipient, message_packet, duration):
        self._duration = duration
        self._timer = 0
        self._destroyed = False
        self._send_message = partial(self.__send_message, recipient, message_packet)

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
    def create_signal(sender, recipient, message) -> UUID:
        duration = (
            SignalFactory.const_time
            if SignalFactory.const_time
            else random.randrange(1, SignalFactory.max_duration + 1)
        )
        message_packet = MessagePacket(sender, message)
        Signal(recipient=recipient, message_packet=message_packet, duration=duration)

        return message_packet.id

    @staticmethod
    def create_response(recipient, packet_id, message):
        duration = (
            SignalFactory.const_time
            if SignalFactory.const_time
            else random.randrange(1, SignalFactory.max_duration + 1)
        )
        message_response = MessageResponse(packet_id, message)
        Signal(recipient=recipient, message_packet=message_response, duration=duration)
