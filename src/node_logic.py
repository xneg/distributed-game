from dataclasses import dataclass

from contracts import RequestType, ClientResponse


@dataclass
class Ping:
    sender_id: int


@dataclass
class Ack:
    sender_id: int


class NodeLogic:
    def __init__(self, node):
        self._id = node.id
        self._send_response = node.send_response
        self._send_message = node.send_message
        self._storage = node.storage
        self._is_leader = node.is_leader
        self._other_nodes = node.other_nodes

    def process_request(self, request):
        if request.type == RequestType.Read:
            value = self._storage.get("x", None)
            self._send_response(
                ClientResponse(
                    type=RequestType.Read,
                    value=value if value is not None else "N",
                    id=request.id,
                )
            )
        else:
            self._storage["x"] = request.value
            self._send_response(
                ClientResponse(type=RequestType.Write, value="+", id=request.id)
            )

    def process_message(self, message):
        if isinstance(message, Ping):
            self._send_message(message.sender_id, Ack(sender_id=self._id))
