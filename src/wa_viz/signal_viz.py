import math

from engine.contracts import (
    ClientWriteRequest,
    ClientReadRequest,
    ClientWriteResponse,
    ClientReadResponse,
)
from wa_viz.utils import SIGNAL_COLOR
from wa_viz.circle import Circle
import pywebcanvas as pwc


class SignalViz:
    radius = 20

    def __init__(self, signal, start, end, canvas):
        self.signal = signal
        self.end = end
        self.start = start
        self.canvas = canvas
        self.x = start[0]
        self.y = start[1]
        self.hovered = False

        message = signal.message
        if isinstance(message, ClientWriteRequest):
            self.info = f"W{message.value}"
        elif isinstance(message, ClientReadRequest):
            self.info = f"R"
        elif isinstance(message, ClientWriteResponse):
            self.info = f"W+"
        elif isinstance(message, ClientReadResponse):
            self.info = f"R{message.value}"
        else:
            self.info = str(signal.message)

    def move(self, progress):
        self.x = (self.end[0] - self.start[0]) * (
            self.signal.progress + self.signal.speed * progress
        ) + self.start[0]
        self.y = (self.end[1] - self.start[1]) * (
            self.signal.progress + self.signal.speed * progress
        ) + self.start[1]

    def draw(self):
        self.canvas.render(Circle(self.x, self.y, SignalViz.radius, SIGNAL_COLOR))
        # self.canvas.fill_style = "black"
        # self.canvas.font = "20px serif"
        if self.hovered:
            self.canvas.render(pwc.Text(self.info, self.x - 10, self.y + 35))

    def set_hovered(self, x, y):
        self.hovered = math.sqrt(math.pow(x - self.x, 2) + math.pow(y - self.y, 2)) <= SignalViz.radius

    def click(self, x, y):
        if self.hovered:
            self.signal.destroy()

    @property
    def coordinates(self):
        return self.x, self.y
