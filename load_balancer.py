from client import ClientRequest, ClientResponse, RequestType
from constant_object import ConstantObject
from link import Link
from singleton import Singleton
from timer import Timer


# class LoadBalancer(ConstantObject, Singleton):
class LoadBalancer(metaclass=Singleton):
    def __init__(self, nodes):
        self._nodes = nodes
        self._leader_node = next(iter([n for n in nodes if n.is_leader()]), None)
        self._timer = Timer()
        self._requests = []
        self._responses = []
        self._round_robin_counter = 0

        print(f"LoadBalancer created at {self._timer.current_epoch()}")

    def add_message(self, message):
        if isinstance(message, ClientRequest):
            self._requests.append(message)
        elif isinstance(message, ClientResponse):
            self._responses.append(message)

        print(f"LoadBalancer accepted {message} at {self._timer.current_epoch()}")

    def process(self):
        for request in self._requests:
            self._process_request(request)

        self._requests = []

        for response in self._responses:
            Link(response.client, response)

        self._responses = []

    def prepared(self):
        return True

    def destroyed(self):
        return False

    def _process_request(self, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        # TODO: should not pass client reference (maybe even id)
        Link(target_node, request)

    def _round_robin(self):
        # TODO: check it
        i = self._round_robin_counter % len(self._nodes)
        self._round_robin_counter = i + 1
        return self._nodes[i]

