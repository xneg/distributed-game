import logging

from contracts import ClientRequest, ClientResponse, RequestType
from link import Link
from timer import Timer


class Node:
    def __init__(self, id, is_leader=False):
        self._id = id
        self._is_leader = is_leader
        self._messages = []
        self._requests = []
        self._timer = Timer()
        self._storage = {}
        logging.info(f"Node {self._id} created at {self._timer.current_epoch()}")

    def add_message(self, sender, message):
        if isinstance(message, ClientRequest):
            self._requests.append((sender, message))
        else:
            self._messages.append((sender, message))

        logging.debug(f"Node {self._id} accepted {message} at {self._timer.current_epoch()}")

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
