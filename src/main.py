import logging

from algorithms.single_client_total_replication import SingleClientTotalReplication
from engine.client import Client, ClientFactory
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory
from engine.signal import SignalFactory
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer

logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
SignalFactory.max_duration = 3
Client.max_pause = 6

if __name__ == "__main__":
    gateway = Gateway(server_id="gateway", timer=Timer())

    node_factory = NodeFactory(SingleClientTotalReplication, gateway)
    nodes = []
    for i in range(0, 3):
        nodes.append(node_factory.add_node())

    # TODO: encapsulate this logic in factory
    for node in nodes:
        for other_node in nodes:
            node.discover(other_node)

    objects = [gateway] + nodes
    simulator = SimulatorLoop(
        timer=Timer(),
        consistency_checker=ConsistencyChecker(),
        objects=objects,
        sleep_interval=0.3,
    )
    client_factory = ClientFactory(gateway)
    for i in range(0, 1):
        client_factory.add_client()

    try:
        simulator.loop()
    except KeyboardInterrupt:
        print("finished!")
