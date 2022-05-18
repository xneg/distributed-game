from engine.contracts import ClientRequest
from engine.node import Node
from engine.utils import generator
from engine.web_server import WebServer


class Gateway(WebServer):
    def __init__(self, server_id, timer, nodes):
        super().__init__(server_id, timer)
        self._leader_node = None
        self._round_robin_counter = 0
        for n in nodes:
            self.discover(n)

    @WebServer.endpoint(ClientRequest)
    # @generator
    def _process_request(self, packet_id, sender_id, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        # self._waiting_responses[request.id] = {"client": sender, "node": target_node}
        channel = self.create_channel(target_node.id, request)
        result = yield from channel
        self.send_message_response(packet_id=packet_id, sender_id=sender_id, response=result)

    # @WebServer.endpoint(ClientResponse)
    # @generator
    # def _process_response(self, sender, response):
    #     if response.id in self._waiting_responses:
    #         wait = self._waiting_responses.pop(response.id)
    #         #  additional check that response received from exact node
    #         SignalFactory.create_signal(self, wait["client"], response)

    def _round_robin(self):
        i = self._round_robin_counter % len(self.nodes)
        self._round_robin_counter = i + 1
        return self.nodes[i]

    @property
    def nodes(self):
        return [s for s in self._other_servers if isinstance(s, Node)]
