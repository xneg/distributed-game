import logging

from client import ClientRequest, ClientResponse
from link import Link
from singleton import Singleton
from timer import Timer


class LoadBalancer(metaclass=Singleton):
    def __init__(self, nodes=None):
        self._nodes = nodes
        self._leader_node = next(iter([n for n in nodes if n.is_leader]), None)
        self._timer = Timer()
        self._requests = []
        self._responses = []
        self._waiting_responses = {}
        self._round_robin_counter = 0

        logging.info(f"LoadBalancer created at {self._timer.current_epoch()}")

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self._requests.append((sender, message))
        elif isinstance(message, ClientResponse):
            self._responses.append((sender, message))

        logging.debug(
            f"LoadBalancer accepted {message} at {self._timer.current_epoch()}"
        )

    def process(self):
        while self._requests:
            (sender, request) = self._requests.pop(0)
            self._process_request(sender, request)

        while self._responses:
            (sender, response) = self._responses.pop(0)
            self._process_response(sender, response)

    def _process_response(self, sender, response):
        if response.id in self._waiting_responses:
            wait = self._waiting_responses.pop(response.id)
            #  additionaly check that response received from exact node
            Link(self, wait["client"], response)

    def _process_request(self, sender, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        self._waiting_responses[request.id] = {"client": sender, "node": target_node}
        Link(self, target_node, request)

    def _round_robin(self):
        # TODO: check it
        i = self._round_robin_counter % len(self._nodes)
        self._round_robin_counter = i + 1
        return self._nodes[i]
