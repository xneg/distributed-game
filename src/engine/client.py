import random
from enum import Enum

from engine.consistency_checker import ConsistencyChecker
from engine.contracts import RequestType, ClientRequest
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from engine.web_server import WebServer


class ClientType(Enum):
    Read = (1,)
    Write = (2,)
    Both = 3


class Client(WebServer):
    max_pause = 1

    def __init__(self, timer, gateway, checker, client_id, client_type=ClientType.Both):
        super().__init__(client_id, timer)
        self.discover(gateway)
        self._gateway_id = gateway.id
        self._checker = checker
        self._type = client_type
        self._waiting = False

    @WebServer.timer(interval=1)
    def _send_request(self):
        if self._waiting:
            return

        self._waiting = True

        request = self._create_request()

        self._checker.add_request(client_id=self.id, request=request)
        channel = self.create_channel(self._gateway_id, request)
        response = yield from channel

        self._checker.add_response(client_id=self.id, response=response)
        for i in range(random.randrange(Client.max_pause) + 1):
            yield
        self._waiting = False

    def _create_request(self):
        request_type = random.choice(list(RequestType))
        if self._type == ClientType.Read:
            request_type = RequestType.Read
        elif self._type == ClientType.Write:
            request_type = RequestType.Write
        value = random.randrange(9) + 1 if request_type == RequestType.Write else None
        request = ClientRequest(request_type, value)
        return request


class ClientFactory:
    def __init__(self, gateway):
        self._current_id = 1
        self._gateway = gateway

    def add_client(self, client_type: ClientType = ClientType.Both):
        client = Client(
            timer=Timer(),
            gateway=self._gateway,
            checker=ConsistencyChecker(),
            client_id="client_" + str(self._current_id),
            client_type=client_type,
        )
        self._gateway.discover(client)
        SimulatorLoop().add_object(client)
        self._current_id = self._current_id + 1
