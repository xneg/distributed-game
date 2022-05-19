from engine.contracts import (
    ClientReadRequest,
    ClientWriteRequest,
    ClientReadResponse,
    ResponseType,
)
from engine.gateway import Gateway
from engine.node import Node
from engine.signal import Signal, SignalFactory


class DummyNode(Node):
    def __init__(self, node_id, timer, is_leader=False):
        super().__init__(node_id, timer, is_leader)
        self.mailbox = []

    @Node.endpoint(message_type=ClientReadRequest)
    def process_read_request(self, request):
        pass

    @Node.endpoint(message_type=ClientWriteRequest)
    def process_write_request(self, request):
        self.mailbox.append(request)


class NodeWithResponse(Node):
    def __init__(self, node_id, timer, response, is_leader=False):
        super().__init__(node_id, timer, is_leader)
        self.response = response

    @Node.endpoint(message_type=ClientReadRequest)
    def process_read_request(self, request):
        return self.response

    @Node.endpoint(message_type=ClientWriteRequest)
    def process_write_request(self, request):
        pass


def test_gateway_resends_request_to_node(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, _ = setup

    node = DummyNode(1, timer)
    gateway = Gateway(server_id="gateway", timer=timer, nodes=[node])
    simulator_loop.add_object(gateway)
    simulator_loop.add_object(node)

    SignalFactory.create_signal(
        sender=sender, recipient=gateway, message=ClientWriteRequest(value=5)
    )

    simulator_loop.process()
    # we need second process because gateway always proceed before any signals
    simulator_loop.process()

    signal = next((o for o in simulator_loop.objects if isinstance(o, Signal)), None)
    assert signal is not None

    # signal reached node
    simulator_loop.process()
    # node processed message
    simulator_loop.process()

    incoming_message = node.mailbox[0]
    assert incoming_message is not None
    assert isinstance(incoming_message, ClientWriteRequest)
    assert incoming_message.value == 5


def test_roundrobin(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, _ = setup

    nodes = [DummyNode(1, timer), DummyNode(2, timer)]

    gateway = Gateway(server_id="gateway", nodes=nodes, timer=timer)
    simulator_loop.add_object(gateway)
    simulator_loop.add_object(nodes[0])
    simulator_loop.add_object(nodes[1])

    SignalFactory.create_signal(sender, gateway, ClientWriteRequest(value=1))
    SignalFactory.create_signal(sender, gateway, ClientWriteRequest(value=2))
    SignalFactory.create_signal(sender, gateway, ClientWriteRequest(value=3))

    # signals reach gateway
    simulator_loop.process()
    # gateway sends signals to nodes
    simulator_loop.process()
    # signals reach nodes
    simulator_loop.process()
    # nodes process request
    simulator_loop.process()

    assert len(nodes[0].mailbox) == 2
    assert len(nodes[1].mailbox) == 1


def test_gateway_resend_response(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, _, recipient = setup

    request = ClientReadRequest()
    response = ClientReadResponse(result=ResponseType.Success, value=1)

    node = NodeWithResponse(node_id=1, timer=timer, response=response)
    gateway = Gateway(server_id="gateway", timer=timer, nodes=[node])
    node.discover(gateway)
    gateway.discover(recipient)

    simulator_loop.add_object(gateway)
    simulator_loop.add_object(node)

    SignalFactory.create_signal(sender=recipient, recipient=gateway, message=request)

    # - 0 1 2 3 4 5 6 7 8
    # N . . . . _ . . . .
    # G . . _ / . \ _ . .
    # C . / . . . . . \ x

    for i in range(0, 7):
        simulator_loop.process()

    assert recipient.mailbox.response == response
