import logging

from algorithms.single_client_sync_replication import SingleClientSyncReplication
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
    node_factory = NodeFactory(SingleClientSyncReplication, gateway)
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

    try:
        simulator.loop()
    except KeyboardInterrupt:
        print("finished!")
