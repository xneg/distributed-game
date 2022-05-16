from engine.contracts import MessagePacket
from engine.node import Node
from engine.signal import SignalFactory
from engine.utils import generator


class TestNode(Node):
    def __init__(self, timer, node_id, is_leader=False):
        super().__init__(timer, node_id, is_leader)
        self.counter = 0
        self.mailbox = None

    @generator
    def process_request(self, request):
        pass

    @generator
    def process_message(self, sender_id: int, message_packet: MessagePacket):
        self.mailbox = message_packet.message
        self.send_message_response(sender_id, message_packet, "Ok")

    @Node.timer(interval=1)
    @generator
    def send_message_timer(self):
        if self.id == 1:
            self.send_message_packet(2, "Hello!")

    @Node.timer(interval=3)
    @generator
    def counter_timer(self):
        self.counter = self.counter + 1

    @Node.timer(interval=1)
    @generator
    def channel_timer(self):
        if self.id == 1:
            channel = self.create_channel(2, "Hello!")
            yield from channel
            self.mailbox = "Ack!"


def test_messaging(setup):
    SignalFactory.const_time = 1

    simulator_loop, timer, _, _ = setup
    node1 = TestNode(timer, 1)
    node2 = TestNode(timer, 2)

    node1.discover_node(node2)
    node2.discover_node(node1)

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
    node = TestNode(timer, 2)

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
    node1 = TestNode(timer, 1)
    node2 = TestNode(timer, 2)

    node1.discover_node(node2)
    node2.discover_node(node1)

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

