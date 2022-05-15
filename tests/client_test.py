import uuid

import pytest

from engine.client import Client, ClientType
from engine.contracts import ClientRequest, RequestType, ClientResponse
from engine.link import Link


class Checker:
    def __init__(self):
        self.response = None

    def add_request(self, client_id, request, time):
        pass

    def add_response(self, client_id, response, time):
        self.response = (client_id, response)


@pytest.fixture
def client_test_setup(setup):
    Client.max_pause = 1
    Link.max_duration = 1
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

    link = next(o for o in simulator_loop.objects if isinstance(o, Link))
    assert link is not None

    simulator_loop.process()

    assert recipient.mailbox is not None
    assert recipient.mailbox[0] == client
    assert isinstance(recipient.mailbox[1], ClientRequest)
    assert recipient.mailbox[1].type == RequestType.Write


def test_client_process_response(client_test_setup):
    simulator_loop, timer, _, recipient, checker = client_test_setup
    client = Client(
        timer=timer,
        gateway=recipient,
        checker=checker,
        client_id=1,
        client_type=ClientType.Read,
    )
    simulator_loop.add_object(client)

    response = ClientResponse(type=RequestType.Read, value=3, id=uuid.uuid4())
    Link(None, client, response)

    simulator_loop.process()
    assert checker.response == (1, response)


def test_client_process_wrong_type_response(client_test_setup):
    simulator_loop, timer, _, recipient, checker = client_test_setup
    client = Client(
        timer=timer,
        gateway=recipient,
        checker=checker,
        client_id=1,
        client_type=ClientType.Write,
    )
    simulator_loop.add_object(client)

    Link(None, client, ClientResponse(type=RequestType.Read, value=3, id=uuid.uuid4()))

    with pytest.raises(TypeError) as excinfo:
        simulator_loop.process()

    assert "Response type doesn't correspond request type!" in str(excinfo.value)
