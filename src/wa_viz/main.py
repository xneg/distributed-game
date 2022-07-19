import asyncio

from engine.client import ClientFactory, Client
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory, Node
from engine.signal import Signal
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from .client_viz import ClientViz
from .gateway_viz import GatewayViz
from .node_viz import NodeViz
from .signal_viz import SignalViz
from .utils import draw_background


class Runner:
    def __init__(self, canvas):
        self._node_type = None
        self._clients_count = 2
        self._nodes_count = 5
        self._finished = False
        self._paused = False
        self._viz_objects = {}
        self.canvas = canvas


    def setup(self, node_type):
        self._node_type = node_type
        self.simulator_timer_interval = 0.3
        self.draw_timer_interval = 1. / 60
        self.ratio = int(self.simulator_timer_interval // self.draw_timer_interval)
        self.simulator = self._create_simulator()
        self.i = 0

    async def run(self):
        self.canvas.clear()
        draw_background(self.canvas)

        if self.i == 0:
            self.simulator.process()

        for o in [o for o in self.simulator.objects if o not in self._viz_objects]:
            self._viz_objects[o] = self._create_viz_object(o, self._viz_objects)

        self._draw_viz_objects(self.i / self.ratio, self.simulator.objects, self._viz_objects)
        if not self._paused:
            self.i = self.i + 1 if self.i < self.ratio else 0
            await asyncio.sleep(self.draw_timer_interval)
        else:
            self.i = 1 if self.i == 0 else self.i
            await asyncio.sleep(self.simulator_timer_interval)

    @property
    def objects_count(self):
        return len(self.simulator.objects)

    def handle_mouse_move(self, e):
        for o in self._viz_objects.values():
            o.set_hovered(e.pageX, e.pageY)

    def _create_simulator(self):
        gateway = Gateway(server_id="gateway", timer=Timer())
        node_factory = NodeFactory(self._node_type, gateway)
        client_factory = ClientFactory(gateway)
        nodes = []
        for i in range(0, self._nodes_count):
            nodes.append(node_factory.add_node())
        clients = []
        for i in range(0, self._clients_count):
            clients.append(client_factory.add_client())
        simulator = SimulatorLoop(
            timer=Timer(),
            consistency_checker=ConsistencyChecker(),
            objects=[gateway] + nodes + clients,
            sleep_interval=0.3,
        )
        return simulator

    def _create_viz_object(self, o, viz_objects):
        if isinstance(o, Gateway):
            return GatewayViz(self.canvas)
        elif isinstance(o, Client):
            return ClientViz(client=o, clients_count=self._clients_count, canvas=self.canvas)
        elif isinstance(o, Node):
            return NodeViz(o, self._nodes_count, self.canvas)
        elif isinstance(o, Signal):
            return SignalViz(
                o,
                viz_objects[o.from_node].coordinates,
                viz_objects[o.to_node].coordinates,
                self.canvas,
            )
        return None

    def _draw_viz_objects(self, progress, objects, viz_objects):
        for (k, v) in viz_objects.copy().items():
            if k in objects:
                v.move(progress)
                v.draw()
            else:
                viz_objects.pop(k)

    def clear(self):
        self.canvas.clear()
        SimulatorLoop.clear()
        Timer.clear()


