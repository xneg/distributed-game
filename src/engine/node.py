import abc
from typing import List, Any

from engine.contracts import ClientReadRequest, ClientWriteRequest, LeaderNotification
from engine.timer import Timer
from engine.web_server import WebServer


class Node(WebServer):
    def __init__(self, node_id, timer, is_leader=False):
        super().__init__(server_id=node_id, timer=timer)
        self.__is_leader = is_leader
        self.__storage = {}
        self.__gateway_id = None

    def discover_gateway(self, web_server: "WebServer"):
        self.discover(web_server)
        self.__gateway_id = web_server.id

    def wait_for_responses(self, request, check_response, count, timeout=-1) -> List[Any]:
        waiting = []

        for node in self.other_nodes:
            waiting.append(self.send_message(node, request))
        responses = yield from self.wait_any(
            waiting, min_count=count, timeout=timeout, condition=check_response
        )
        return [r for r in responses if r is not None]

    @property
    def is_leader(self):
        return self.__is_leader

    @property
    def other_nodes(self):
        return [
            k for (k, v) in self._other_servers.items() if issubclass(type(v), Node)
        ]

    @property
    def storage(self):
        return self.__storage

    @property
    def local_time(self):
        return self.__local_timer

    def notify_leadership(self):
        self.send_message(self.__gateway_id, LeaderNotification(id=self.id))

    @WebServer.endpoint(message_type=ClientReadRequest)
    @abc.abstractmethod
    def process_read_request(self, request):
        pass

    @WebServer.endpoint(message_type=ClientWriteRequest)
    @abc.abstractmethod
    def process_write_request(self, request):
        pass


class NodeFactory:
    def __init__(self, node_class, gateway):
        self._current_id = 0
        self._node_class = node_class
        self._gateway = gateway
        self._nodes = []

    def add_node(self, is_leader=False):
        self._current_id = self._current_id + 1
        node = self._node_class(
            timer=Timer(),
            node_id=self._current_id,
            is_leader=is_leader,
        )
        node.discover_gateway(self._gateway)
        self._gateway.discover(node)

        for n in self._nodes:
            n.discover(node)
            node.discover(n)

        self._nodes.append(node)
        return node
