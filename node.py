from contracts import ClientRequest, ClientResponse, RequestType
from constant_object import ConstantObject
from link import Link
from timer import Timer


class Node(ConstantObject):
    def __init__(self, node_id, is_leader=False):
        self._node_id = node_id
        self._is_leader = is_leader
        self._messages = []
        self._requests = []
        self._timer = Timer()
        self._storage = {}

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self._requests.append((sender, message))
        else:
            self._messages.append((sender, message))

        print(f"Node {self._node_id} accepted {message} at {self._timer.current_epoch()}")

    def is_leader(self):
        return self._is_leader

    def process(self):
        while self._requests:
            (sender, request) = self._requests.pop(0)
            self._process_request(sender, request)

        self._messages = []

    def _process_request(self, sender, request):
        if request.type == RequestType.Read:
            value = self._storage.get("x", None)
            Link(self, sender, ClientResponse(type=RequestType.Read, value=value, id=request.id))
        else:
            self._storage["x"] = request.value
            Link(self, sender, ClientResponse(type=RequestType.Write, value="SUCCESS", id=request.id))
