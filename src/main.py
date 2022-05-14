import logging

from engine.client import Client, ClientFactory
from engine.consistency_checker import ConsistencyChecker
from engine.link import Link
from engine.gateway import Gateway
from engine.node import Node
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer

logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
Link.max_duration = 3
Client.max_pause = 6

if __name__ == "__main__":
    nodes = [Node(1), Node(2), Node(3)]
    # nodes = [Node(1)]
    for node in nodes:
        for other_node in nodes:
            node.discover_node(other_node)

    objects = [Gateway(nodes=nodes)] + nodes
    simulator = SimulatorLoop(
        timer=Timer(),
        consistency_checker=ConsistencyChecker(),
        objects=objects,
        sleep_interval=0.3,
    )
    client_factory = ClientFactory()
    for i in range(0, 3):
        client_factory.add_client()
    try:
        simulator.loop()
    except KeyboardInterrupt:
        print("finished!")
