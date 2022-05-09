import logging
import random

from contracts import ClientResponse, RequestType, ClientRequest
from link import Link
from load_balancer import LoadBalancer
from consistency_checker import ConsistencyChecker
from timer import Timer


class Client:
    def __init__(self, client_id):
        self._id = client_id
        self._request = None
        self._response = None
        self._waiting = False
        self._timer = Timer()
        self._checker = ConsistencyChecker()
        self._balancer = LoadBalancer()
        logging.info(f"Client {self._id} created at {self._timer.current_epoch()}")

    def add_message(self, sender, response: ClientResponse):
        logging.debug(
            f"Client {self._id} received {response} at {self._timer.current_epoch()}"
        )
        self._response = response
        self._checker.add_response(
            client_id=self._id, response=response, time=self._timer.current_epoch()
        )
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
        self._request = ClientRequest(request_type, value)

        logging.debug(
            f"Client {self._id} sent {self._request} at {self._timer.current_epoch()}"
        )
        Link(self, self._balancer, self._request)
        self._checker.add_request(
            client_id=self._id, request=self._request, time=self._timer.current_epoch()
        )
        self._waiting = True
