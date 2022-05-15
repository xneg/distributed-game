from engine.signal import Signal


def test_message_delivered_in_time(setup):
    simulator_loop, timer, sender, recipient = setup

    Signal(sender, recipient, "Hello!", 5)

    for i in range(0, 5):
        assert recipient.mailbox is None
        simulator_loop.process()

    assert recipient.mailbox == (sender, "Hello!")
    assert timer.current_epoch() == 5


def test_signal_destroyed_after_message_delivered(setup):
    simulator_loop, _, sender, recipient = setup

    signal = Signal(sender, recipient, "Hello!", 5)

    assert signal in simulator_loop.objects

    for i in range(0, 5):
        simulator_loop.process()

    assert simulator_loop.objects == []
