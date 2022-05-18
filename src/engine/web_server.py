import abc
import logging
from typing import List, Any, Dict
from uuid import UUID

from engine.contracts import MessagePacket, MessageResponse
from engine.signal import SignalFactory
from engine.utils import make_timer, make_endpoint


class Channel:
    def __init__(self):
        self._trigger = False
        self._response = None

    def trigger(self, response):
        self._trigger = True
        self._response = response

    def wait(self):
        # TODO: Need to add timeout or other break conditions
        while not self._trigger:
            yield None  # print(f"processing {self._message.id}")
        return self._response


class WebServer(abc.ABC):
    timer = make_timer()
    endpoint = make_endpoint()

    def __init__(self, server_id, timer):
        self.__id = server_id
        self.__global_timer = timer
        self.__timer_handlers = self.timer.all

        class_name = f"{type(self).__module__}.{type(self).__name__}"
        self.__endpoint_handlers = self.endpoint.all[class_name]
        self.__local_timer = 1

        self.__message_packets: List[MessagePacket] = []
        self._other_servers: Dict[Any, WebServer] = {}
        self.__storage = {}
        self.__generators = []
        self.__channels = {}

        logging.info(
            f"{self.__id} created at {self.__global_timer.current_epoch()}"
        )

    def discover(self, web_server: 'WebServer'):
        if self != web_server:
            self._other_servers[web_server.id] = web_server

    def add_message(self, message):
        if isinstance(message, MessageResponse):
            channel = self.__channels.pop(message.id, None)
            if channel:
                channel.trigger(message.response)
        elif isinstance(message, MessagePacket):
            self.__message_packets.append(message)

        logging.debug(
            f"{self.__id} accepted {message} at {self.__global_timer.current_epoch()}"
        )

    def process(self):
        while self.__message_packets:
            packet = self.__message_packets.pop(0)
            message_type = type(packet.message)
            handler = self.__endpoint_handlers[message_type]
            self.__generators.append(handler(self, packet.id, packet.sender.id, packet.message))

        for (handler, interval) in self.__timer_handlers:
            if self.__local_timer % interval == 0:
                self.__generators.append(handler(self))

        for g in self.__generators.copy():
            try:
                next(g)
            except StopIteration:
                self.__generators.remove(g)

        self.__local_timer = self.__local_timer + 1

    def create_channel(self, server_id, message):
        if server_id not in self._other_servers:
            raise Exception(f"Server with id {server_id} doesn't exists!")

        packet = MessagePacket(sender=self, message=message)
        channel = Channel()
        self.__channels[packet.id] = channel
        SignalFactory.create_signal(
            self, self._other_servers[server_id], packet
        )  # json.dumps(message_packet))

        return channel.wait()

    def send_message_packet(self, server_id, message):
        self.create_channel(server_id, message)

    def send_message_response(self, packet_id: UUID, sender_id: Any, response):
        SignalFactory.create_signal(
            self,
            self._other_servers[sender_id],
            MessageResponse(packet_id, response),
        )

    # @abc.abstractmethod
    # @generator
    # def process_message(self, sender_id: int, message):
    #     pass

    @property
    def id(self):
        return self.__id
