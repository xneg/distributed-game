import pytest

from engine.gateway import Gateway
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer


class Sender:
    pass


class Recipient:
    def __init__(self):
        self.mailbox = None

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
    Gateway.clear()
