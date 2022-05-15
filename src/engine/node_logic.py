import abc
from abc import ABC

from engine.utils import make_timer, generator


# For now, this class is not used
class NodeLogic(ABC):
    # timer = make_timer()

    def __init__(
            self,
            id,
            send_response,
            send_message,
            create_channel,
            storage,
            is_leader,
            other_nodes,
    ):
        self._id = id
        self._send_response = send_response
        self._send_message = send_message
        self._create_channel = create_channel
        self._storage = storage
        self._is_leader = is_leader
        self._other_nodes = other_nodes

    @abc.abstractmethod
    @generator
    def process_request(self, request):
        pass

    @abc.abstractmethod
    @generator
    def process_message(self, message):
        pass

    # @timer(interval=5)
    # @generator
    # def some_timer(self):
    #     print(f"Node {self._id} timer fired")
    #
    # @timer(interval=10)
    # @generator
    # def second_timer(self):
    #     print(f"Node {self._id} AAAAAAAAAAAAAAA")
    # for node in self._other_nodes:
    #     self._send_message(node, Ping(sender_id=self._id))
