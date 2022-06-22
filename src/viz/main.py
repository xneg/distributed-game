import time

from IPython.core.display_functions import display
from ipycanvas import Canvas, hold_canvas

from algorithms.single_client_total_replication import SingleClientTotalReplication
from engine.client import ClientFactory
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer


def run():
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

    canvas = Canvas()

    display(canvas)

    # objects = simulator.objects
    try:
        while True:
            simulator.process()
            objects = simulator.objects
            with hold_canvas():
                canvas.clear()
                canvas.font = "32px serif"
                canvas.fill_text(len(objects), 10, 32)
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("finished!")
