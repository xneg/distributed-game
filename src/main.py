import logging

from client import Client
from link import Link
from load_balancer import LoadBalancer
from node import Node
from simulator_loop import SimulatorLoop

logging.basicConfig()
# logging.getLogger().setLevel(logging.INFO)
Link.max_duration = 3

if __name__ == '__main__':
    nodes = [Node(1), Node(2), Node(3)]
    for node in nodes:
        for other_node in nodes:
            node.discover_node(other_node)

    objects = [LoadBalancer(nodes=nodes), Client(1), Client(2), Client(3), Client(4)] + nodes
    simulator = SimulatorLoop(objects=objects, sleep_interval=0.5)
    try:
        simulator.loop()
    except KeyboardInterrupt:
        print("finished!")
