import random

from constant_object import ConstantObject
from contracts import ClientResponse, RequestType, ClientRequest
from link import Link
from load_balancer import LoadBalancer
from timer import Timer


class Client(ConstantObject):
    def __init__(self, client_id):
        self._id = client_id
        self._request = None
        self._response = None
        self._waiting = False
        self._timer = Timer()
        # TODO: replace print with logger
        print(f"Client {self._id} created at {self._timer.current_epoch()}")

    def add_message(self, sender, response: ClientResponse):
        print(f"Client {self._id} received {response} at {self._timer.current_epoch()}")
        self._response = response
        if self._response.type != self._request.type:
            raise TypeError("Response type doesn't correspond request type!")

    def process(self):
        if self._response:
            self._waiting = False
        self._response = None

        if not self._waiting:
            self._send_request()

    def _send_request(self):
        request_type = random.choice(list(RequestType))
        value = random.randrange(10) if request_type == RequestType.Write else None
        self._request = ClientRequest(self, request_type, value)

        print(
            f"Client {self._id} sent {self._request} at {self._timer.current_epoch()}"
        )
        Link(self, LoadBalancer(), self._request)
        self._waiting = True
