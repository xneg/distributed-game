import abc
import logging
from abc import ABC

from engine.contracts import ClientRequest, MessageAck, MessagePacket, generator, make_timer
from engine.signal import SignalFactory
from engine.timer import Timer


class Channel:
    def __init__(self, node, node_id, message):
        self._node = node
        self._node_id = node_id
        self._message = message

    def wait(self):
        # TODO: Need to add timeout or other break conditions
        while self._message.id in self._node._channels:
            yield  # print(f"processing {self._message.id}")


class Node(ABC):
    timer = make_timer()

    def __init__(self, timer, node_id, is_leader=False):
        self._id = node_id
        self._is_leader = is_leader
        self._global_timer = timer

        self._messages = []
        self._requests = []
        self._waiting_responses = {}
        self._storage = {}
        self._other_nodes = {}

        self._timer_handlers = self.timer.all
        self._generators = []
        self._channels = set()

        logging.info(f"Node {self._id} created at {self._global_timer.current_epoch()}")

    def discover_node(self, node):
        if self != node:
            self._other_nodes[node.id] = node

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self._waiting_responses[message.id] = sender
            self._requests.append(message)
        elif isinstance(message, MessageAck):
            self._channels.remove(message.id)
        elif isinstance(message, MessagePacket):
            self._messages.append(message.message)
            SignalFactory.create_signal(sender=self, recipient=sender, message=MessageAck(message))

        logging.debug(
            f"Node {self._id} accepted {message} at {self._global_timer.current_epoch()}"
        )

    def process(self):
        while self._requests:
            request = self._requests.pop(0)
            self._generators.append(self.process_request(request))

        while self._messages:
            message = self._messages.pop(0)
            self._generators.append(self.process_message(message))

        for (handler, interval) in self._timer_handlers:
            # TODO: rewrite using local timer
            if self._global_timer.current_epoch() % interval == 0:
                self._generators.append(handler(self))

        for g in self._generators.copy():
            try:
                next(g)
            except StopIteration:
                self._generators.remove(g)

    def send_response(self, response):
        if response.id not in self._waiting_responses:
            raise Exception("You response not to your request!")
        gateway = self._waiting_responses.pop(response.id)
        SignalFactory.create_signal(self, gateway, response)

    def create_channel(self, node_id, message):
        if node_id not in self._other_nodes:
            raise Exception(f"Node with id {node_id} doesn't exists!")

        packet = MessagePacket(message)
        self._channels.add(packet.id)
        SignalFactory.create_signal(self, self._other_nodes[node_id], packet)  # json.dumps(message))

        return Channel(self, node_id, packet)

    def send_message(self, node_id, message):
        self.create_channel(node_id, message)

    @property
    def id(self):
        return self._id

    @property
    def is_leader(self):
        return self._is_leader

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
