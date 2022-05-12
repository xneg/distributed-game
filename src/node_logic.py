from dataclasses import dataclass

from contracts import RequestType, ClientResponse, make_timer, generator


@dataclass
class Ping:
    sender_id: int


@dataclass
class Ack:
    sender_id: int


class NodeLogic:
    timer = make_timer()

    def __init__(
        self, id, send_response, send_message, storage, is_leader, other_nodes
    ):
        self._id = id
        self._send_response = send_response
        self._send_message = send_message
        self._storage = storage
        self._is_leader = is_leader
        self._other_nodes = other_nodes

    @generator
    def process_request(self, request):
        if request.type == RequestType.Read:
            value = self._storage.get("x", None)
            yield
            self._send_response(
                ClientResponse(
                    type=RequestType.Read,
                    value=value if value is not None else "N",
                    id=request.id,
                )
            )
        else:
            self._storage["x"] = request.value
            yield
            self._send_response(
                ClientResponse(type=RequestType.Write, value="+", id=request.id)
            )

    @generator
    def process_message(self, message):
        if isinstance(message, Ping):
            self._send_message(message.sender_id, Ack(sender_id=self._id))
        elif isinstance(message, Ack):
            print(f"Node {self._id} received ack from {message.sender_id}")

    @timer(interval=10)
    def some_timer(self):
        for node in self._other_nodes:
            self._send_message(node, Ping(sender_id=self._id))
