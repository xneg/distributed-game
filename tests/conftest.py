import pytest

from simulator_loop import SimulatorLoop
from timer import Timer


@pytest.fixture(scope="function", autouse=True)
def clear_singletons():
    SimulatorLoop.clear()
    Timer.clear()
