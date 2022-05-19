import abc
import logging
from typing import List, Any, Dict
from uuid import UUID

from engine.signal import SignalFactory, MessagePacket, MessageResponse
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

        class_name = f"{type(self).__module__}.{type(self).__name__}"
        self.__endpoint_handlers = (
            self.endpoint.all[class_name] if class_name in self.endpoint.all else {}
        )
        self.__timer_handlers = (
            self.timer.all[class_name] if class_name in self.timer.all else []
        )
        self.__local_timer = 1

        self.__message_packets: List[MessagePacket] = []
        self._other_servers: Dict[Any, WebServer] = {}
        self.__storage = {}
        self.__generators = []
        self.__channels = {}

        logging.info(f"{self.__id} created at {self.__global_timer.current_epoch()}")

    def discover(self, web_server: "WebServer"):
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

    def __process_request(self, handler, packet_id, sender_id, message):
        result = yield from handler(self, message)
        if result:
            self.__send_message_response(packet_id, sender_id, result)

    def process(self):
        while self.__message_packets:
            packet = self.__message_packets.pop(0)
            message_type = type(packet.message)
            try:
                handler = self.__endpoint_handlers[message_type]
            except Exception as e:
                # TODO: raise understandable error
                print(self.__class__)
                raise
            self.__generators.append(
                self.__process_request(
                    handler, packet.id, packet.sender.id, message=packet.message
                )
            )

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

        #  TODO: add logging
        # logging.debug(
        #     f"Client {self.id} sent {request} at {self.timer.current_epoch()}"
        # )
        packet_id = SignalFactory.create_signal(
            self, self._other_servers[server_id], message
        )  # json.dumps(message_packet))
        channel = Channel()
        self.__channels[packet_id] = channel
        return channel.wait()

    def send_message_packet(self, server_id, message):
        self.create_channel(server_id, message)

    def __send_message_response(self, packet_id: UUID, sender_id: Any, response):
        SignalFactory.create_response(
            self._other_servers[sender_id], packet_id, response
        )

    # @abc.abstractmethod
    # @generator
    # def process_message(self, sender_id: int, message):
    #     pass

    @property
    def id(self):
        return self.__id
