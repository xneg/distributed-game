import pytest

from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer


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


@pytest.fixture(scope="function", autouse=True)
def clear_singletons():
    SimulatorLoop.clear()
    Timer.clear()
