import logging

from client import Client, ClientFactory, ClientType
from link import Link
from load_balancer import LoadBalancer
from node import Node
from simulator_loop import SimulatorLoop

logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
Link.max_duration = 3
Client.max_pause = 6

if __name__ == '__main__':
    nodes = [Node(1), Node(2), Node(3)]
    # nodes = [Node(1)]
    for node in nodes:
        for other_node in nodes:
            node.discover_node(other_node)

    objects = [LoadBalancer(nodes=nodes)] + nodes
    simulator = SimulatorLoop(objects=objects, sleep_interval=0.3)
    client_factory = ClientFactory()
    for i in range(0, 3):
        client_factory.add_client()
    try:
        simulator.loop()
    except KeyboardInterrupt:
        print("finished!")
