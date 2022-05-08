# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



# Press the green button in the gutter to run the script.
from client import Client
from load_balancer import LoadBalancer
from simulator_loop import SimulatorLoop

if __name__ == '__main__':
    load_balancer = LoadBalancer()
    clients = [Client(1, load_balancer), Client(2, load_balancer)]
    simulator = SimulatorLoop(load_balancer=load_balancer, clients=clients)
    simulator.loop()
