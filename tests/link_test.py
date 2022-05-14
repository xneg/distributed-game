import pytest

from link import Link
from simulator_loop import SimulatorLoop


class Sender:
    pass


class Recipient:
    def __init__(self):
        self.mailbox = None

    def add_message(self, sender, message):
        self.mailbox = (sender, message)


@pytest.fixture
def setup():
    simulator_loop = SimulatorLoop(sleep_interval=0)
    sender = Sender()
    recipient = Recipient()

    assert simulator_loop.objects == []
    return simulator_loop, sender, recipient


def test_message_delivered(setup):
    simulator_loop, sender, recipient = setup

    Link(sender, recipient, "Hello!", 5)

    for i in range(0, 6):
        assert recipient.mailbox is None
        simulator_loop.process()

    assert recipient.mailbox == (sender, "Hello!")


def test_link_destroyed_after_message_delivered(setup):
    simulator_loop, sender, recipient = setup

    link = Link(sender, recipient, "Hello!", 5)

    assert link in simulator_loop.objects

    for i in range(0, 6):
        simulator_loop.process()

    assert simulator_loop.objects == []
