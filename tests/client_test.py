from client import Client, ClientType
from contracts import ClientRequest, RequestType
from link import Link
from timer import Timer


class Checker:
    def add_request(self, client_id, request, time):
        pass


def test_client_sends_messages(setup):
    simulator_loop, _, recipient = setup
    client = Client(
        timer=Timer(),
        gateway=recipient,
        checker=Checker(),
        client_id=1,
        client_type=ClientType.Write,
    )
    Client.max_pause = 0
    Link.max_duration = 1

    simulator_loop.add_object(client)
    simulator_loop.process()

    link = next(o for o in simulator_loop.objects if isinstance(o, Link))
    assert link is not None

    simulator_loop.process()

    assert recipient.mailbox is not None
    assert recipient.mailbox[0] == client
    assert isinstance(recipient.mailbox[1], ClientRequest)
    assert recipient.mailbox[1].type == RequestType.Write

