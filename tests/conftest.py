import pytest

from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer


class Sender:
    @property
    def id(self):
        return "Sender"


class Recipient:
    def __init__(self):
        self.mailbox = None

    @property
    def id(self):
        return "Recipient"

    def add_message(self, message):
        self.mailbox = message


@pytest.fixture
def setup():
    timer = Timer()
    simulator_loop = SimulatorLoop(timer=timer, sleep_interval=0)
    sender = Sender()
    recipient = Recipient()

    assert simulator_loop.objects == []
    return simulator_loop, timer, sender, recipient


@pytest.fixture(scope="function", autouse=True)
def clear_singletons():
    SimulatorLoop.clear()
    Timer.clear()
