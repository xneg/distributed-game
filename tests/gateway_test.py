import uuid

from engine.contracts import ClientRequest, RequestType, ClientResponse, MessagePacket
from engine.gateway import Gateway
from engine.node import Node
from engine.signal import Signal, SignalFactory


class DummyNode(Node):
    def __init__(self, server_id, timer):
        super().__init__(server_id, timer)
        self.mailbox = None

    @Node.endpoint(message_type=ClientRequest)
    def process_request(self, _, sender_id, request):
        self.mailbox = (sender_id, request)


def test_gateway_resends_request_to_node(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, _ = setup

    recipient = DummyNode(1, timer)
    gateway = Gateway(server_id="gateway", timer=timer, nodes=[recipient])
    simulator_loop.add_object(gateway)
    simulator_loop.add_object(recipient)

    message_packet = MessagePacket(sender=sender, message=ClientRequest(RequestType.Read))
    Signal(gateway, message_packet, duration=1)
    simulator_loop.process()
    # we need second process because gateway always proceed before any signals
    simulator_loop.process()

    signal = next((o for o in simulator_loop.objects if isinstance(o, Signal)), None)
    assert signal is not None

    # signal reached node
    simulator_loop.process()
    # node processed message
    simulator_loop.process()

    assert recipient.mailbox is not None
    assert recipient.mailbox[0] == 'gateway'
    assert isinstance(recipient.mailbox[1], ClientRequest)
    assert recipient.mailbox[1].type == RequestType.Read


def test_roundrobin(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, _ = setup

    nodes = [DummyNode(1, timer), DummyNode(2, timer)]

    gateway = Gateway(server_id="gateway", nodes=nodes, timer=timer)
    simulator_loop.add_object(gateway)

    Signal(gateway, ClientRequest(RequestType.Write, value=1), duration=1)
    Signal(gateway, ClientRequest(RequestType.Write, value=2), duration=1)
    Signal(gateway, ClientRequest(RequestType.Write, value=3), duration=1)
    simulator_loop.process()
    # we need second process because gateway always proceed before any signals
    simulator_loop.process()
    simulator_loop.process()

    assert len(nodes[0].mailbox) == 2
    assert len(nodes[1].mailbox) == 1


def test_gateway_resend_response(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, recipient = setup
    gateway = Gateway(nodes=[DummyNode()], timer=timer)

    simulator_loop.add_object(gateway)

    request = ClientRequest(RequestType.Read)
    response = ClientResponse(RequestType.Read, value=1, id=request.id)
    Signal(sender=recipient, recipient=gateway, message_packet=request, duration=1)
    Signal(sender, gateway, message_packet=response, duration=1)

    # signals are reaching gateway
    simulator_loop.process()
    # gateway processed signals and generates own signals
    simulator_loop.process()
    # recipient processed signal from gateway
    simulator_loop.process()

    assert recipient.mailbox == (gateway, response)


def test_gateway_will_not_resend_response_without_request(setup):
    SignalFactory.const_time = 1
    simulator_loop, timer, sender, recipient = setup
    gateway = Gateway(nodes=[DummyNode()], timer=timer)

    simulator_loop.add_object(gateway)

    response = ClientResponse(RequestType.Read, value=1, id=uuid.uuid4())
    Signal(sender, gateway, message_packet=response, duration=1)

    # signals are reaching gateway
    simulator_loop.process()
    # gateway processed signals and doesn't generate own signal
    simulator_loop.process()
    # recipient doesn't receive anything
    simulator_loop.process()

    assert recipient.mailbox is None
