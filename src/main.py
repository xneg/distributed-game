import logging

from client import Client
from load_balancer import LoadBalancer
from node import Node
from simulator_loop import SimulatorLoop

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':
    nodes = [Node(1), Node(2), Node(3)]
    objects = [LoadBalancer(nodes=nodes), Client(1), Client(2)] + nodes
    simulator = SimulatorLoop(objects=objects, sleep_interval=0.5)
    simulator.loop()
