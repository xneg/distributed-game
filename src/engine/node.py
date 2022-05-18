import abc

from engine.contracts import ClientRequest
from engine.timer import Timer
from engine.web_server import WebServer


class Node(WebServer):
    def __init__(self, node_id, timer, is_leader=False):
        super().__init__(server_id=node_id, timer=timer)
        self.__is_leader = is_leader
        self.__storage = {}

    def send_response(self, response):
        pass
        # if response.id not in self.__waiting_responses:
        #     raise Exception("You response not to your request!")
        # gateway = self.__waiting_responses.pop(response.id)
        # SignalFactory.create_signal(self, gateway, response)

    @property
    def is_leader(self):
        return self.__is_leader

    @property
    def other_nodes(self):
        return self._other_servers.keys()

    @property
    def storage(self):
        return self.__storage

    @property
    def local_time(self):
        return self.__local_timer

    @WebServer.endpoint(message_type=ClientRequest)
    @abc.abstractmethod
    # @generator
    def process_request(self, request):
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
