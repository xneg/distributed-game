from engine.contracts import ClientWriteRequest, ClientReadRequest
from engine.node import Node
from engine.web_server import WebServer


class Gateway(WebServer):
    def __init__(self, server_id, timer, nodes):
        super().__init__(server_id, timer)
        self._leader_node = None
        self._round_robin_counter = 0
        for n in nodes:
            self.discover(n)

    @WebServer.endpoint(ClientWriteRequest)
    def _process_request(self, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        channel = self.create_channel(target_node.id, request)
        result = yield from channel
        return result

    @WebServer.endpoint(ClientReadRequest)
    def _process_request(self, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        channel = self.create_channel(target_node.id, request)
        result = yield from channel
        return result

    def _round_robin(self):
        i = self._round_robin_counter % len(self.nodes)
        self._round_robin_counter = i + 1
        return self.nodes[i]

    @property
    def nodes(self):
        return [s for s in self._other_servers.values() if issubclass(type(s), Node)]
