import time

from ipycanvas import hold_canvas

from algorithms.single_client_total_replication import SingleClientTotalReplication
from engine.client import ClientFactory, Client
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory, Node
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from viz.utils import draw_client, draw_background, draw_node


def run(background, nodes_layer):
    gateway = Gateway(server_id="gateway", timer=Timer())
    node_factory = NodeFactory(SingleClientTotalReplication, gateway)
    client_factory = ClientFactory(gateway)

    nodes = []
    for i in range(0, 3):
        nodes.append(node_factory.add_node())

    clients = []
    for i in range(0, 1):
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
            with hold_canvas(nodes_layer):
                nodes_layer.reset_transform()
                nodes_layer.clear()
                for idx, c in enumerate(clients):
                    draw_client(nodes_layer, idx, c.id, len(clients))
                nodes_layer.translate(nodes_layer.width // 2, nodes_layer.height // 4)
                for idx, n in enumerate(nodes):
                    draw_node(nodes_layer, idx, n.id, len(nodes))
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("finished!")
