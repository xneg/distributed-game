from simulator_loop import SimulatorLoop
from timer import Timer


def test_timer_process():
    simulator_loop = SimulatorLoop(timer=Timer(), sleep_interval=0)

    assert Timer().current_epoch() == 0

    for i in range(0, 7):
        simulator_loop.process()

    assert Timer().current_epoch() == 7


def test_timer_singleton():
    a = Timer()
    b = Timer()

    a.process()
    assert b.current_epoch() == 1