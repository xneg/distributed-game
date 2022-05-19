import uuid

import pytest

from engine.client import Client, ClientType
from engine.contracts import ClientRequest, RequestType, ClientResponse
from engine.signal import Signal, SignalFactory
from engine.web_server import WebServer


class Checker:
    def __init__(self):
        self.response = None

    def add_request(self, client_id, request):
        pass

    def add_response(self, client_id, response):
        self.response = (client_id, response)


class TestGateway(WebServer):
    @WebServer.endpoint(ClientRequest)
    def _process_request(self, packet_id, sender_id, request: ClientRequest):
        response = ClientResponse(request.type, 5, request.id)
        self.send_message_response(
            packet_id=packet_id, sender_id=sender_id, response=response
        )


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
    assert isinstance(recipient.mailbox.message, ClientRequest)
    assert recipient.mailbox.message.type == RequestType.Write


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
