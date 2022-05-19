import pytest

from engine.client import Client, ClientType
from engine.contracts import (
    ClientReadRequest,
    ClientReadResponse,
    ResponseType,
    ClientWriteRequest,
    ClientWriteResponse,
)
from engine.signal import Signal, SignalFactory
from engine.web_server import WebServer


class Checker:
    def __init__(self):
        self.response = None

    def add_event(self, client_id, event):
        self.response = (client_id, event)


class TestGateway(WebServer):
    @WebServer.endpoint(ClientReadRequest)
    def _process_read_request(self, _: ClientReadRequest):
        return ClientReadResponse(result=ResponseType.Success, value=5)

    @WebServer.endpoint(ClientWriteRequest)
    def _process_write_request(self, _: ClientWriteRequest):
        return ClientWriteResponse(result=ResponseType.Success)


@pytest.fixture
def client_test_setup(setup):
    Client.max_pause = 1
    SignalFactory.const_time = 1
    return *setup, Checker()


def test_client_sends_messages(client_test_setup):
    simulator_loop, timer, _, recipient, checker = client_test_setup
    client = Client(
        timer=timer,
        gateway=recipient,
        checker=checker,
        client_id=1,
        client_type=ClientType.Write,
    )

    simulator_loop.add_object(client)
    simulator_loop.process()

    signal = next(o for o in simulator_loop.objects if isinstance(o, Signal))
    assert signal is not None

    simulator_loop.process()

    assert recipient.mailbox is not None
    assert isinstance(recipient.mailbox.message, ClientWriteRequest)


def test_client_process_response(client_test_setup):
    simulator_loop, timer, _, _, checker = client_test_setup

    gateway = TestGateway("test_gateway", timer)
    client = Client(
        timer=timer,
        gateway=gateway,
        checker=checker,
        client_id=1,
        client_type=ClientType.Read,
    )
    gateway.discover(client)

    simulator_loop.add_object(client)
    simulator_loop.add_object(gateway)

    simulator_loop.process()
    simulator_loop.process()
    simulator_loop.process()


# def test_client_process_response(client_test_setup):
#     simulator_loop, timer, _, recipient, checker = client_test_setup
#     client = Client(
#         timer=timer,
#         gateway=recipient,
#         checker=checker,
#         client_id=1,
#         client_type=ClientType.Read,
#     )
#     simulator_loop.add_object(client)
#
#     response = ClientResponse(type=RequestType.Read, value=3, id=uuid.uuid4())
#     SignalFactory.create_signal(None, client, response)
#
#     simulator_loop.process()
#     assert checker.response == (1, response)
#
#
# def test_client_process_wrong_type_response(client_test_setup):
#     simulator_loop, timer, _, recipient, checker = client_test_setup
#     client = Client(
#         timer=timer,
#         gateway=recipient,
#         checker=checker,
#         client_id=1,
#         client_type=ClientType.Write,
#     )
#     simulator_loop.add_object(client)
#
#     SignalFactory.create_signal(
#         None, client, ClientResponse(type=RequestType.Read, value=3, id=uuid.uuid4())
#     )
#
#     with pytest.raises(TypeError) as excinfo:
#         simulator_loop.process()
#
#     assert "Response type doesn't correspond request type!" in str(excinfo.value)
