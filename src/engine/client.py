import logging
import random
from enum import Enum

from engine.contracts import ClientResponse, RequestType, ClientRequest
from engine.signal import Signal
from engine.gateway import Gateway
from engine.consistency_checker import ConsistencyChecker
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer


class ClientType(Enum):
    Read = (1,)
    Write = (2,)
    Both = 3


class Client:
    max_pause = 1

    def __init__(self, timer, gateway, checker, client_id, client_type=ClientType.Both):
        self._timer = timer
        self._gateway = gateway
        self._checker = checker
        self._id = client_id
        self._type = client_type
        self._pending_request = None
        self._waiting = False

        self._send_time = self._get_send_time()
        logging.info(f"Client {self._id} created at {self._timer.current_epoch()}")

    def add_message(self, _, response: ClientResponse):
        logging.debug(
            f"Client {self._id} received {response} at {self._timer.current_epoch()}"
        )

        if response.type != self._pending_request.type:
            raise TypeError("Response type doesn't correspond request type!")

        self._checker.add_response(
            client_id=self._id, response=response, time=self._timer.current_epoch()
        )

        self._waiting = False
        self._send_time = self._get_send_time()

    def process(self):
        if not self._waiting and self._send_time <= self._timer.current_epoch():
            self._send_request()

    def _send_request(self):
        request_type = random.choice(list(RequestType))
        if self._type == ClientType.Read:
            request_type = RequestType.Read
        elif self._type == ClientType.Write:
            request_type = RequestType.Write

        value = random.randrange(9) + 1 if request_type == RequestType.Write else None
        self._pending_request = ClientRequest(request_type, value)

        logging.debug(
            f"Client {self._id} sent {self._pending_request} at {self._timer.current_epoch()}"
        )
        Signal(self, self._gateway, self._pending_request)
        self._checker.add_request(
            client_id=self._id, request=self._pending_request, time=self._timer.current_epoch()
        )
        self._waiting = True

    def _get_send_time(self):
        return random.randrange(Client.max_pause) + self._timer.current_epoch()


class ClientFactory:
    def __init__(self):
        self._current_id = 1

    def add_client(self, client_type: ClientType = ClientType.Both):
        SimulatorLoop().add_object(
            Client(
                timer=Timer(),
                gateway=Gateway(),
                checker=ConsistencyChecker(),
                client_id=self._current_id,
                client_type=client_type,
            )
        )
        self._current_id = self._current_id + 1
