from dataclasses import dataclass
from enum import Enum
import random
from typing import Any

from constant_object import ConstantObject
from link import Link
from timer import Timer


class RequestType(Enum):
    Read = 1,
    Write = 2


@dataclass(frozen=True)
class ClientRequest:
    client: Any
    type: RequestType
    value: int = None


@dataclass(frozen=True)
class ClientResponse:
    client: Any
    type: RequestType
    value: Any


class Client(ConstantObject):
    def __init__(self, client_id, load_balancer):
        self._id = client_id
        self._responses = []
        self._waiting = False
        self._timer = Timer()
        # TODO: extract contracts and use load_balancer as singleton
        self._load_balancer = load_balancer
        # TODO: replace print with logger
        print(f"Client {self._id} created at {self._timer.current_epoch()}")

    def add_message(self, response: ClientResponse):
        print(f"Client {self._id} received {response} at {self._timer.current_epoch()}")
        self._responses.append(response)

    def process(self):
        if self._responses:
            self._waiting = False
        self._responses = []

        if not self._waiting:
            self._send_request()

    def _send_request(self):
        request_type = random.choice(list(RequestType))
        value = random.randrange(10) if request_type == RequestType.Write else None
        request = ClientRequest(self, request_type, value)

        print(f"Client {self._id} sent {request} at {self._timer.current_epoch()}")
        Link(self._load_balancer, request)
        self._waiting = True
