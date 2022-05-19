from dataclasses import dataclass

from engine.contracts import RequestType, ClientResponse, ClientRequest
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

    @WebServer.endpoint(message_type=ClientRequest)
    def process_request(self, request):
        if request.type == RequestType.Read:
            print(f"Node {self.id} received read request")
            value = self.storage.get("x", None)
            return ClientResponse(
                type=RequestType.Read,
                value=value if value is not None else "N",
                id=request.id,
            )
        else:
            print(f"Node {self.id} received write request")
            self.storage["x"] = request.value
            channels = []

            for node in self.other_nodes:
                channels.append(
                    self.create_channel(node, WriteRequest(value=request.value))
                )

            for c in channels:
                yield from c

            print(f"Node {self.id} sent write response")
            return ClientResponse(type=RequestType.Write, value="+", id=request.id)

    # @timer(interval=5)
    # @generator
    # def some_timer(self):
    #     print(f"Node {self.__id} timer fired")
    #
    # @Node.timer(interval=10)
    # @generator
    # def second_timer(self):
    #     print(f"Node {self.__id} AAAAAAAAAAAAAAA")
    # for node in self.__other_nodes:
    #     self._send_message(node, Ping(sender_id=self.__id))
