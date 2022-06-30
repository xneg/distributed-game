import random
from enum import Enum

from engine.consistency_checker import ConsistencyChecker
from engine.contracts import ClientReadRequest, ClientWriteRequest, ClientReadResponse, ClientWriteResponse
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
        self._state = ''

    @WebServer.timer(interval=1)
    def _send_request(self):
        if self._waiting:
            return

        self._waiting = True

        request = self._create_request()

        self._checker.add_event(client_id=self.id, event=request)
        response = self.send_message(self._gateway_id, request).wait()
        response = yield from response

        if isinstance(response, ClientReadResponse):
            self._state = "R" + str(response.value)
        elif isinstance(response, ClientWriteResponse):
            self._state = "W+"

        self._checker.add_event(client_id=self.id, event=response)
        for i in range(random.randrange(Client.max_pause) + 1):
            yield
        self._waiting = False

    def _create_request(self):
        request_type = self.choose_request_type()
        if request_type == RequestType.Read:
            return ClientReadRequest()
        else:
            value = (
                random.randrange(9) + 1 if request_type == RequestType.Write else None
            )
            return ClientWriteRequest(value)

    def choose_request_type(self):
        request_type = random.choice(list(RequestType))
        if self._type == ClientType.Read:
            request_type = RequestType.Read
        elif self._type == ClientType.Write:
            request_type = RequestType.Write
        return request_type

    @property
    def state(self):
        return self._state


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
        self._current_id = self._current_id + 1
        return client


class RequestType(Enum):
    Read = (1,)
    Write = 2
