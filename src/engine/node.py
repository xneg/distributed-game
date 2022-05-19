import abc

from engine.contracts import ClientRequest
from engine.timer import Timer
from engine.web_server import WebServer


class Node(WebServer):
    def __init__(self, node_id, timer, is_leader=False):
        super().__init__(server_id=node_id, timer=timer)
        self.__is_leader = is_leader
        self.__storage = {}

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

    @WebServer.endpoint(message_type=ClientRequest)
    @abc.abstractmethod
    def process_request(self, packet_id, sender_id, request):
        pass


class NodeFactory:
    def __init__(self, node_class):
        self._current_id = 0
        self._node_class = node_class

    def add_node(self, is_leader=False):
        self._current_id = self._current_id + 1
        return self._node_class(
            timer=Timer(),
            node_id=self._current_id,
            is_leader=is_leader,
        )
