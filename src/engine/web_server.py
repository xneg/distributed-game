import abc
import logging
from typing import List, Any, Dict
from uuid import UUID

from engine.signal import SignalFactory, MessagePacket, MessageResponse
from engine.utils import make_timer, make_endpoint


class WaitingResponse:
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
        self.__waiting_responses = {}

        logging.info(f"{self.__id} created at {self.__global_timer.current_epoch()}")

    def discover(self, web_server: "WebServer"):
        if self != web_server:
            self._other_servers[web_server.id] = web_server

    def add_message(self, message):
        if isinstance(message, MessageResponse):
            waiting_response = self.__waiting_responses.pop(message.id, None)
            if waiting_response:
                waiting_response.trigger(message.response)
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
            except KeyError:
                raise KeyError(
                    f"{self.__class__} doesn't have endpoint for {message_type}"
                )
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

    def get_response(self, server_id, message):
        if server_id not in self._other_servers:
            raise Exception(f"Server with id {server_id} doesn't exists!")

        logging.debug(
            f"{self.id} sent {message} to {server_id} at {self.timer.current_epoch()}"
        )
        packet_id = SignalFactory.create_signal(
            self, self._other_servers[server_id], message
        )  # json.dumps(message_packet))
        waiting_response = WaitingResponse()
        self.__waiting_responses[packet_id] = waiting_response
        return waiting_response.wait()

    def send_message(self, server_id, message):
        self.get_response(server_id, message)

    def __send_message_response(self, packet_id: UUID, sender_id: Any, response):
        SignalFactory.create_response(
            self._other_servers[sender_id], packet_id, response
        )

    @property
    def id(self):
        return self.__id
