# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



# Press the green button in the gutter to run the script.
from client import Client
from load_balancer import LoadBalancer
from node import Node
from simulator_loop import SimulatorLoop

if __name__ == '__main__':
    nodes = [Node(1), Node(2, is_leader=True), Node(3)]
    objects = [LoadBalancer(nodes=nodes), Client(1), Client(2)] + nodes
    simulator = SimulatorLoop(objects=objects)
    simulator.loop()
