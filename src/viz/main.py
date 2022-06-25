import time

from ipycanvas import hold_canvas

from algorithms.single_client_versioned_majority import SingleClientVersionedMajority
from engine.client import ClientFactory, Client, ClientType
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory, Node
from engine.signal import Signal
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from viz.utils import draw_client, draw_background, draw_node, draw_signal, draw_gateway


def run(client_count, nodes_count, background, nodes_layer, signals_layer):
    simulator_timer_interval = 0.3
    draw_timer_interval = 0.02
    ratio = int(simulator_timer_interval // draw_timer_interval)

    gateway = Gateway(server_id="gateway", timer=Timer())
    node_factory = NodeFactory(SingleClientVersionedMajority, gateway)
    client_factory = ClientFactory(gateway)

    nodes = []
    for i in range(0, nodes_count):
        nodes.append(node_factory.add_node())

    clients = []
    for i in range(0, client_count):
        clients.append(client_factory.add_client())

    simulator = SimulatorLoop(
        timer=Timer(),
        consistency_checker=ConsistencyChecker(),
        objects=[gateway] + nodes + clients,
        sleep_interval=0.3,
    )

    draw_background(background)

    try:
        while True:
            simulator.process()
            objects = simulator.objects
            clients = [o for o in objects if isinstance(o, Client)]
            nodes = [o for o in objects if issubclass(type(o), Node)]
            signals = [o for o in objects if isinstance(o, Signal)]

            object_positions = draw_nodes(clients, nodes, gateway, nodes_layer)

            # TODO: should distinguish between simulator time and draw time
            # time.sleep(0.3)
            for i in range(0, ratio):
                draw_signals(object_positions, signals, i / ratio, signals_layer)
                time.sleep(draw_timer_interval)
    except KeyboardInterrupt:
        print("finished!")


def draw_signals(object_positions, signals, draw_progress, canvas):
    with hold_canvas(canvas):
        canvas.reset_transform()
        canvas.clear()

        # This will not work with both clients and nodes
        # canvas.translate(canvas.width // 2, canvas.height // 4)
        for s in signals:
            if s.from_node not in object_positions or s.to_node not in object_positions:
                continue
            draw_signal(
                canvas,
                object_positions[s.from_node],
                object_positions[s.to_node],
                s.progress + s.speed * draw_progress,
            )


def draw_nodes(clients, nodes, gateway, canvas):
    with hold_canvas(canvas):
        canvas.reset_transform()
        canvas.clear()

        object_positions = {}

        for idx, c in enumerate(clients):
            object_positions[c.id] = draw_client(canvas, idx, c.id, len(clients))
        object_positions[gateway.id] = draw_gateway(canvas)

        # canvas.translate(canvas.width // 2, canvas.height // 4)
        center = (canvas.width // 2, canvas.height // 4)
        for idx, n in enumerate(nodes):
            object_positions[n.id] = draw_node(canvas, center, idx, n.id, len(nodes))
    return object_positions
