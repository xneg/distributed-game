import abc
import logging
from abc import ABC

from engine.contracts import ClientRequest, MessageAck, MessagePacket
from engine.utils import make_timer, generator
from engine.signal import SignalFactory
from engine.timer import Timer


class Channel:
    def __init__(self):
        self._trigger = False

    def trigger(self):
        self._trigger = True

    def wait(self):
        # TODO: Need to add timeout or other break conditions
        while not self._trigger:
            yield  # print(f"processing {self._message.id}")


class Node(ABC):
    timer = make_timer()

    def __init__(self, timer, node_id, is_leader=False):
        self.__id = node_id
        self.__is_leader = is_leader
        self.__global_timer = timer
        self.__local_timer = 1

        self.__messages = []
        self.__requests = []
        self.__waiting_responses = {}
        self.__storage = {}
        self.__other_nodes = {}

        self.__timer_handlers = self.timer.all
        self.__generators = []
        self.__channels = {}

        logging.info(
            f"Node {self.__id} created at {self.__global_timer.current_epoch()}"
        )

    def discover_node(self, node):
        if self != node:
            self.__other_nodes[node.id] = node

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self.__waiting_responses[message.id] = sender
            self.__requests.append(message)
        elif isinstance(message, MessageAck):
            channel = self.__channels.pop(message.id, None)
            if channel:
                channel.trigger()

        elif isinstance(message, MessagePacket):
            self.__messages.append(message.message)
            SignalFactory.create_signal(
                sender=self, recipient=sender, message=MessageAck(message)
            )

        logging.debug(
            f"Node {self.__id} accepted {message} at {self.__global_timer.current_epoch()}"
        )

    def process(self):
        while self.__requests:
            request = self.__requests.pop(0)
            self.__generators.append(self.process_request(request))

        while self.__messages:
            message = self.__messages.pop(0)
            self.__generators.append(self.process_message(message))

        for (handler, interval) in self.__timer_handlers:
            if self.__local_timer % interval == 0:
                self.__generators.append(handler(self))

        for g in self.__generators.copy():
            try:
                next(g)
            except StopIteration:
                self.__generators.remove(g)

        self.__local_timer = self.__local_timer + 1

    def send_response(self, response):
        if response.id not in self.__waiting_responses:
            raise Exception("You response not to your request!")
        gateway = self.__waiting_responses.pop(response.id)
        SignalFactory.create_signal(self, gateway, response)

    def create_channel(self, node_id, message):
        if node_id not in self.__other_nodes:
            raise Exception(f"Node with id {node_id} doesn't exists!")

        packet = MessagePacket(message)
        channel = Channel()
        self.__channels[packet.id] = channel
        SignalFactory.create_signal(
            self, self.__other_nodes[node_id], packet
        )  # json.dumps(message))

        return channel.wait()

    def send_message(self, node_id, message):
        self.create_channel(node_id, message)

    @property
    def id(self):
        return self.__id

    @property
    def is_leader(self):
        return self.__is_leader

    @property
    def other_nodes(self):
        return self.__other_nodes.keys()

    @property
    def storage(self):
        return self.__storage

    @property
    def local_time(self):
        return self.__local_timer

    @abc.abstractmethod
    @generator
    def process_request(self, request):
        pass

    @abc.abstractmethod
    @generator
    def process_message(self, message):
        pass


class NodeFactory:
    def __init__(self, node_class):
        self._current_id = 0
        self._node_class = node_class

    def add_node(self, is_leader=False):
        self._current_id = self._current_id + 1
        return self._node_class(
            timer=Timer(),
            node_id=self._current_id,
            is_leader=is_leader,
        )
