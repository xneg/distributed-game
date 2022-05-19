from engine.contracts import ClientWriteRequest, ClientReadRequest
from engine.node import Node
from engine.web_server import WebServer


class Gateway(WebServer):
    def __init__(self, server_id, timer):
        super().__init__(server_id, timer)
        self._leader_node = None
        self._round_robin_counter = 0

    @WebServer.endpoint(ClientWriteRequest)
    def _process_write_request(self, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        waiting_response = self.get_response(target_node.id, request)
        result = yield from waiting_response
        return result

    @WebServer.endpoint(ClientReadRequest)
    def _process_read_request(self, request):
        target_node = self._leader_node if self._leader_node else self._round_robin()
        waiting_response = self.get_response(target_node.id, request)
        result = yield from waiting_response
        return result

    def _round_robin(self):
        i = self._round_robin_counter % len(self.nodes)
        self._round_robin_counter = i + 1
        return self.nodes[i]

    @property
    def nodes(self):
        return [s for s in self._other_servers.values() if issubclass(type(s), Node)]
