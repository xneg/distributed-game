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
class NodeWriteRequest:
    value: int


class SingleClientSyncReplication(Node):
    @WebServer.endpoint(message_type=NodeWriteRequest)
    def process_node_write_request(self, request: NodeWriteRequest):
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

        waiting_tasks = []

        for node in self.other_nodes:
            waiting_tasks.append(
                self.send_message(node, NodeWriteRequest(value=request.value))
            )

        yield from self.wait_all(waiting_tasks)

        print(f"Node {self.id} sent write response")
        return ClientWriteResponse(result=ResponseType.Success)
