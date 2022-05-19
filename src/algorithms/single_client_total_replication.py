from dataclasses import dataclass

from engine.contracts import RequestType, ClientResponse, ClientRequest
from engine.node import Node
from engine.web_server import WebServer


@dataclass
class WriteRequest:
    value: int


class SingleClientTotalReplication(Node):
    @WebServer.endpoint(message_type=WriteRequest)
    def process_message(self, packet_id, sender_id, request: WriteRequest):
        self.storage["x"] = request.value
        self.send_message_response(packet_id, sender_id, "Ack")

    @WebServer.endpoint(message_type=ClientRequest)
    def process_request(self, packet_id, sender_id, request):
        if request.type == RequestType.Read:
            print(f"Node {self.id} received read request")
            value = self.storage.get("x", None)
            self.send_message_response(
                packet_id=packet_id,
                sender_id=sender_id,
                response=ClientResponse(
                    type=RequestType.Read,
                    value=value if value is not None else "N",
                    id=request.id,
                ),
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

            self.send_message_response(
                packet_id=packet_id,
                sender_id=sender_id,
                response=ClientResponse(
                    type=RequestType.Write, value="+", id=request.id
                ),
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
