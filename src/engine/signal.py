import random
import uuid
from functools import partial
from uuid import UUID

from engine.simulator_loop import SimulatorLoop


class MessagePacket:
    def __init__(self, sender, message):
        self._sender = sender
        self._message = message
        self._id = uuid.uuid4()

    @property
    def sender(self):
        return self._sender

    @property
    def message(self):
        return self._message

    @property
    def id(self):
        return self._id


class MessageResponse:
    def __init__(self, id: UUID, response):
        self._id = id
        self._response = response

    @property
    def id(self):
        return self._id

    @property
    def response(self):
        return self._response


class Signal:
    max_duration = 10

    def __init__(self, recipient, message_packet, duration):
        self._duration = duration
        self._timer = 0
        self._destroyed = False
        self._send_message = partial(self.__send_message, recipient, message_packet)
        self._from = None
        self._to = None
        self._message_packet = message_packet

        SimulatorLoop().add_object(self)

    def process(self):
        self._timer = self._timer + 1

        if self._timer == self._duration:
            self._send_message()
            self._destroyed = True

    def destroyed(self):
        return self._destroyed

    # TODO: do this more elegant
    def set_from_to(self, from_node, to_node):
        self._from = from_node
        self._to = to_node

    @property
    def from_node(self):
        return self._from

    @property
    def to_node(self):
        return self._to

    @property
    def progress(self):
        return self._timer / self._duration

    @property
    def speed(self):
        return 1 / self._duration

    @property
    def message(self):
        if isinstance(self._message_packet, MessagePacket):
            return self._message_packet.message
        if isinstance(self._message_packet, MessageResponse):
            return self._message_packet.response

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
        signal = Signal(recipient=recipient, message_packet=message_packet, duration=duration)
        # TODO: BAD CODE!
        signal.set_from_to(sender, recipient)
        return message_packet.id

    @staticmethod
    def create_response(sender, recipient, packet_id, message):
        duration = (
            SignalFactory.const_time
            if SignalFactory.const_time
            else random.randrange(1, SignalFactory.max_duration + 1)
        )
        message_response = MessageResponse(packet_id, message)
        signal = Signal(recipient=recipient, message_packet=message_response, duration=duration)
        # TODO: BAD CODE!
        signal.set_from_to(sender, recipient)
