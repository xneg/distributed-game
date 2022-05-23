from engine.node import Node
from engine.signal import SignalFactory


class TestNode(Node):
    def __init__(self, node_id, timer, is_leader=False):
        super().__init__(node_id, timer, is_leader)
        self.counter = 0
        self.mailbox = None

    @Node.endpoint(message_type=str)
    def process_message(self, message):
        self.mailbox = message
        return "Ok"

    @Node.timer(interval=1)
    def send_message_timer(self):
        if self.id == 1:
            self.send_message(2, "Hello!")

    @Node.timer(interval=3)
    def counter_timer(self):
        self.counter = self.counter + 1

    @Node.timer(interval=1)
    def waiting_timer(self):
        if self.id == 1:
            response = self.send_message(2, "Hello!")
            yield from response
            self.mailbox = "Ack!"


def test_messaging(setup):
    SignalFactory.const_time = 1

    simulator_loop, timer, _, _ = setup
    node1 = TestNode(1, timer)
    node2 = TestNode(2, timer)

    node1.discover(node2)
    node2.discover(node1)

    simulator_loop.add_object(node1)
    simulator_loop.add_object(node2)

    # node 1 sends signal due to timer
    simulator_loop.process()
    # signal reaches to node 2
    simulator_loop.process()
    assert node2.mailbox is None
    # node 2 processed signal
    simulator_loop.process()

    assert node2.mailbox == "Hello!"


def test2_local_timer(setup):
    simulator_loop, timer, _, _ = setup
    node = TestNode(2, timer)

    simulator_loop.process()
    simulator_loop.process()

    simulator_loop.add_object(node)

    for i in range(0, 8):
        simulator_loop.process()

    assert node.counter == 2
    simulator_loop.process()
    assert node.counter == 3


def test3_yields(setup):
    SignalFactory.const_time = 1

    simulator_loop, timer, _, _ = setup
    node1 = TestNode(1, timer)
    node2 = TestNode(2, timer)

    node1.discover(node2)
    node2.discover(node1)

    simulator_loop.add_object(node1)
    simulator_loop.add_object(node2)

    # node 1 sends signal due to timer
    simulator_loop.process()
    # signal reaches to node 2
    simulator_loop.process()
    # node 2 processed signal
    simulator_loop.process()
    # node 1 receives response
    simulator_loop.process()

    assert node1.mailbox is None
    # node 1 processed  response
    simulator_loop.process()
    #
    assert node1.mailbox == "Ack!"
