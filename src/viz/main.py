import time

from ipycanvas import hold_canvas
from ipywidgets import Output

from engine.client import ClientFactory, Client, ClientType
from engine.consistency_checker import ConsistencyChecker
from engine.gateway import Gateway
from engine.node import NodeFactory, Node
from engine.signal import Signal, SignalFactory
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from viz.client_viz import ClientViz
from viz.gateway_viz import GatewayViz
from viz.node_viz import NodeViz
from viz.signal_viz import SignalViz
from viz.utils import draw_background


class Runner:
    out = Output()

    def __init__(self, clients_count, nodes_count, canvas, node_type, fps=60, step_interval=0.3):
        self._finished = False
        self._paused = False
        self.elapsed_time = 0
        self.elapsed_steps = 0

        self._clients_count = clients_count
        self._nodes_count = nodes_count
        self._background = canvas[0]
        self._nodes_layer = canvas[1]
        self._signals_layer = canvas[2]
        self._node_type = node_type

        self._viz_objects = {}
        self.dt_s = 1.0 / fps
        self.simulator = self._create_simulator()

        self.step_interval = step_interval

        canvas.on_key_down(self.handle_keyboard_event)
        canvas.on_mouse_move(self.handle_mouse_move)
        canvas.on_mouse_down(self.handle_mouse_down)

    def run(self):
        draw_background(self._background)

        while not self._finished:
            t0 = time.time()

            self.step()

            t1 = time.time()
            delta = t1 - t0
            if delta < self.dt_s:
                time.sleep(self.dt_s - delta)

        SimulatorLoop.clear()
        Timer.clear()

    def step(self):
        if not self._paused:
            self.elapsed_time = self.elapsed_time + self.dt_s

            if self.elapsed_time > (self.elapsed_steps + 1) * self.step_interval:
                self.simulator.process()
                self.elapsed_steps = self.elapsed_steps + 1

            for o in [o for o in self.simulator.objects if o not in self._viz_objects]:
                self._viz_objects[o] = self._create_viz_object(o, self._viz_objects)

        progress = (
            self.elapsed_time - self.elapsed_steps * self.step_interval
        ) / self.step_interval
        self._draw_viz_objects(max(progress, 0), self.simulator.objects, self._viz_objects)

    @out.capture()
    def handle_keyboard_event(self, key, shift_key, ctrl_key, meta_key):
        if key == " ":
            self._paused = not self._paused
        if key == "Escape":
            self._finished = True

    @out.capture()
    def handle_mouse_move(self, x, y):
        for o in self._viz_objects.values():
            o.set_hovered(x, y)

    @out.capture()
    def handle_mouse_down(self, x, y):
        try:
            for o in self._viz_objects.values():
                o.click(x, y)
        except Exception as e:
            print(e)

    @property
    def get_out(self):
        return self.out

    def _create_simulator(self):
        SignalFactory.min_duration = 3
        SignalFactory.min_duration = 7

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
            return GatewayViz(self._nodes_layer)
        elif isinstance(o, Node):
            return NodeViz(o, self._nodes_count, self._nodes_layer)
        elif isinstance(o, Client):
            return ClientViz(o, self._clients_count, self._nodes_layer)
        elif isinstance(o, Signal):
            return SignalViz(
                o,
                viz_objects[o.from_node].coordinates,
                viz_objects[o.to_node].coordinates,
                self._signals_layer,
            )

    def _draw_viz_objects(self, progress, objects, viz_objects):
        with hold_canvas():
            self._nodes_layer.clear()
            self._signals_layer.clear()
            for (k, v) in viz_objects.copy().items():
                if k in objects:
                    v.move(progress)
                    v.draw()
                else:
                    viz_objects.pop(k)
