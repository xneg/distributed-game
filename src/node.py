import logging

from contracts import ClientRequest
from link import Link
from node_logic import NodeLogic
from timer import Timer


class Channel:
    def __init__(self, node, node_id, message):
        self._node = node
        self._node_id = node_id
        self._message = message
        self._node.send_message(node_id=self._node_id, message=self._message)

    def wait(self):
        self._node.send_message(node_id=self._node_id, message=self._message)
        while not self._check_response(message_id=self._message.id):
            yield print(f"processing {self._message.id}")

    # TODO: Need to add timeout or other break conditions
    def _check_response(self, message_id):
        x = next((m for m in self._node._messages if m.id == message_id), None)
        if x is not None:
            print(f"Strange message {x}")
        return x


class Node:
    def __init__(self, node_id, is_leader=False):
        self._id = node_id
        self._is_leader = is_leader
        self._timer = Timer()

        self._messages = []
        self._requests = []
        self._waiting_responses = {}
        self._storage = {}
        self._other_nodes = {}

        self._logic = NodeLogic(
            id=self.id,
            send_response=self.send_response,
            send_message=self.send_message,
            create_channel=self.create_channel,
            storage=self.storage,
            is_leader=self.is_leader,
            other_nodes=self.other_nodes,
        )

        self._timer_handlers = [] # self._logic.timer.all
        self._generators = []

        logging.info(f"Node {self._id} created at {self._timer.current_epoch()}")

    def discover_node(self, node):
        if self != node:
            self._other_nodes[node.id] = node

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self._waiting_responses[message.id] = sender
            self._requests.append(message)
        else:
            self._messages.append(message)

        logging.debug(
            f"Node {self._id} accepted {message} at {self._timer.current_epoch()}"
        )

    def process(self):
        while self._requests:
            request = self._requests.pop(0)
            self._generators.append(self._logic.process_request(request))

        while self._messages:
            message = self._messages.pop(0)
            self._generators.append(self._logic.process_message(message))

        for g in self._generators.copy():
            try:
                next(g)
            except StopIteration:
                self._generators.remove(g)

        for (handler, interval) in self._timer_handlers:
            if self._timer.current_epoch() % interval == 0:
                handler(self._logic)

    def send_response(self, response):
        if response.id not in self._waiting_responses:
            raise Exception("You response not to your request!")
        gateway = self._waiting_responses.pop(response.id)
        Link(self, gateway, response)

    def send_message(self, node_id, message):
        if node_id not in self._other_nodes:
            raise Exception(f"Node with id {node_id} doesn't exists!")

        Link(self, self._other_nodes[node_id], message) # json.dumps(message))

    def create_channel(self, node_id, message):
        return Channel(self, node_id, message)

    @property
    def id(self):
        return self._id

    @property
    def is_leader(self):
        return self._is_leader

    @property
    def storage(self):
        return self._storage

    @property
    def other_nodes(self):
        return self._other_nodes.keys()
