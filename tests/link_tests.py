from link import Link
from simulator_loop import SimulatorLoop


class Sender:
    pass


class Recipient:
    def __init__(self):
        self.mailbox = None

    def add_message(self, sender, message):
        self.mailbox = (sender, message)


def test_message_delivered():
    simulator_loop = SimulatorLoop(sleep_interval=0)
    sender = Sender()
    recipient = Recipient()
    Link(sender, recipient, "Hello!", 5)

    for i in range(0, 6):
        assert recipient.mailbox is None
        simulator_loop.process()

    assert recipient.mailbox == (sender, "Hello!")

