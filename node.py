from client import ClientRequest, ClientResponse, RequestType
from constant_object import ConstantObject
from link import Link
from timer import Timer


class Node(ConstantObject):
    def __init__(self, node_id):
        self._node_id = node_id
        self._messages = []
        self._requests = []
        self._timer = Timer()
        self._storage = {}

    def add_message(self, message):
        if isinstance(message, ClientRequest):
            self._requests.append(message)
        else:
            self._messages.append(message)

        print(f"Node {self._node_id} accepted {message} at {self._timer.current_epoch()}")

    def is_leader(self):
        return False

    def process(self):
        for request in self._requests:
            self.process_request(request)
        self._requests = []
        self._messages = []

    def process_request(self, request):
        if request.type == RequestType.Read:
            value = self._storage.get("x", None)
            Link(request.client, ClientResponse(request.client, RequestType.Read, value))
        else:
            self._storage["x"] = request.value
            Link(request.client, ClientResponse(request.client, RequestType.Write, "SUCCESS"))
