from dataclasses import dataclass

from engine.contracts import (
    ClientReadRequest,
    ClientReadResponse,
    ResponseType,
    ClientWriteRequest,
    ClientWriteResponse,
)
from engine.node import Node
from engine.web_server import WebServer


@dataclass
class WriteRequest:
    value: int


class SingleClientTotalReplication(Node):
    @WebServer.endpoint(message_type=WriteRequest)
    def process_message(self, request: WriteRequest):
        self.storage["x"] = request.value
        return "Ack"

    @WebServer.endpoint(message_type=ClientReadRequest)
    def process_read_request(self, request: ClientReadRequest):
        print(f"Node {self.id} received read request")
        value = self.storage.get("x", None)
        return ClientReadResponse(
            result=ResponseType.Success, value=value if value is not None else "N"
        )

    @WebServer.endpoint(message_type=ClientWriteRequest)
    def process_write_request(self, request: ClientWriteRequest):
        print(f"Node {self.id} received write request")
        self.storage["x"] = request.value
        waiting_responses = []

        for node in self.other_nodes:
            waiting_responses.append(
                self.wait_response(node, WriteRequest(value=request.value))
            )

        for r in waiting_responses:
            yield from r

        print(f"Node {self.id} sent write response")
        return ClientWriteResponse(result=ResponseType.Success)
