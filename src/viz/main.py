import time

from ipycanvas import hold_canvas
from ipywidgets import Output

from algorithms.single_client_versioned_majority import SingleClientVersionedMajority
from engine.client import ClientFactory, Client, ClientType
from engine.consistency_checker import ConsistencyChecker
from engine.contracts import ClientWriteRequest, ClientReadRequest, ClientWriteResponse, ClientReadResponse
from engine.gateway import Gateway
from engine.node import NodeFactory, Node
from engine.signal import Signal
from engine.simulator_loop import SimulatorLoop
from engine.timer import Timer
from viz.utils import draw_client, draw_background, draw_node, draw_signal, draw_gateway


class Runner:
    out = Output()

    def __init__(self, clients_count, nodes_count, canvas):
        self._finished = False
        self._paused = False
        self._clients_count = clients_count
        self._nodes_count = nodes_count
        self._background = canvas[0]
        self._nodes_layer = canvas[1]
        self._signals_layer = canvas[2]
        canvas.on_key_down(self.on_keyboard_event)

    def run(self):
        simulator_timer_interval = 0.3
        draw_timer_interval = 0.02
        ratio = int(simulator_timer_interval // draw_timer_interval)

        gateway = Gateway(server_id="gateway", timer=Timer())
        node_factory = NodeFactory(SingleClientVersionedMajority, gateway)
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

        draw_background(self._background)

        try:
            while True:
                if self._finished:
                    raise KeyboardInterrupt
                if self._paused:
                    continue
                simulator.process()
                objects = simulator.objects
                clients = [o for o in objects if isinstance(o, Client)]
                nodes = [o for o in objects if issubclass(type(o), Node)]
                signals = [o for o in objects if isinstance(o, Signal)]

                object_positions = _draw_nodes(clients, nodes, gateway, self._nodes_layer)

                # TODO: should distinguish between simulator time and draw time
                # time.sleep(0.3)
                for i in range(0, ratio):
                    _draw_signals(object_positions, signals, i / ratio, self._signals_layer)
                    time.sleep(draw_timer_interval)
        except KeyboardInterrupt:
            print("finished!")
            SimulatorLoop.clear()
            Timer.clear()

    @out.capture()
    def on_keyboard_event(self, key, shift_key, ctrl_key, meta_key):
        if key == ' ':
            self._paused = not self._paused
        if key == 'Escape':
            self._finished = True

    @property
    def get_out(self):
        return self.out


def _draw_signals(object_positions, signals, draw_progress, canvas):
    with hold_canvas(canvas):
        canvas.reset_transform()
        canvas.clear()

        for s in signals:
            info = ''
            message = s.message
            if isinstance(message, ClientWriteRequest):
                info = f"W{message.value}"
            elif isinstance(message, ClientReadRequest):
                info = f"R"
            elif isinstance(message, ClientWriteResponse):
                info = f"W+"
            elif isinstance(message, ClientReadResponse):
                info = f"R{message.value}"
            else:
                info = str(s.message)

            draw_signal(
                canvas,
                info,
                object_positions[s.from_node],
                object_positions[s.to_node],
                s.progress + s.speed * draw_progress,
            )


def _draw_nodes(clients, nodes, gateway, canvas):
    with hold_canvas(canvas):
        canvas.reset_transform()
        canvas.clear()

        object_positions = {}

        for idx, c in enumerate(clients):
            object_positions[c.id] = draw_client(canvas, idx, c.id, len(clients))
        object_positions[gateway.id] = draw_gateway(canvas)

        # canvas.translate(canvas.width // 2, canvas.height // 4)
        center = (canvas.width // 2, canvas.height // 4)
        for idx, n in enumerate(nodes):
            object_positions[n.id] = draw_node(canvas, center, idx, n.id, str(n.storage), len(nodes))
    return object_positions
