from dataclasses import dataclass

from engine.contracts import RequestType, ClientResponse
from engine.utils import generator
from engine.node import Node


@dataclass
class WriteRequest:
    value: int


class SingleClientTotalReplication(Node):

    @generator
    def process_message(self, message):
        if isinstance(message, WriteRequest):
            self.storage["x"] = message.value

    @generator
    def process_request(self, request):
        if request.type == RequestType.Read:
            print(f"Node {self.id} received read request")
            value = self.storage.get("x", None)
            self.send_response(
                ClientResponse(
                    type=RequestType.Read,
                    value=value if value is not None else "N",
                    id=request.id,
                )
            )
        else:
            print(f"Node {self.id} received write request")
            self.storage["x"] = request.value
            channels = []

            for node in self.other_nodes:
                channels.append(self.create_channel(node, WriteRequest(value=request.value)))

            for c in channels:
                yield from c

            self.send_response(
                ClientResponse(type=RequestType.Write, value="+", id=request.id)
            )
            print(f"Node {self.id} sent write response")

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