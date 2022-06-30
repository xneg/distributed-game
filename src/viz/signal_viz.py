from engine.contracts import (
    ClientWriteRequest,
    ClientReadRequest,
    ClientWriteResponse,
    ClientReadResponse,
)
from viz.utils import SIGNAL_COLOR


class SignalViz:
    def __init__(self, signal, start, end, canvas):
        self.signal = signal
        self.end = end
        self.start = start
        self.canvas = canvas
        self.x = start[0]
        self.y = start[1]

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
        self.canvas.fill_style = SIGNAL_COLOR
        self.canvas.fill_circle(self.x, self.y, 20)
        self.canvas.fill_style = "black"
        self.canvas.font = "20px serif"
        self.canvas.fill_text(self.info, self.x - 10, self.y + 5)

    @property
    def coordinates(self):
        return self.x, self.y
