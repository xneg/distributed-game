import math

from wa_viz.utils import NODE_COLOR
from wa_viz.circle import Circle
import pywebcanvas as pwc


class NodeViz:
    def __init__(self, node, nodes_count, canvas):
        self.node = node
        self.canvas = canvas
        self.x = 0
        self.y = 0

        self._set_position(nodes_count, int(self.node.id))

    def move(self, progress):
        pass

    def draw(self):
        self.canvas.render(Circle(self.x, self.y, 30, NODE_COLOR))
        self.canvas.render(pwc.Text(self.node.id, self.x - 7, self.y + 7))
        self.canvas.render(pwc.Text(str(self.node.storage), self.x - 15, self.y + 50))

    def set_hovered(self, x, y):
        pass

    def click(self, x, y):
        pass

    @property
    def coordinates(self):
        return self.x, self.y

    def _set_position(self, nodes_count, index):
        center = (self.canvas.width // 2, self.canvas.height // 4)
        r = 120
        t = math.pi * 2 / nodes_count * index
        self.x = r * math.cos(t - math.pi / 2) + center[0]
        self.y = r * math.sin(t - math.pi / 2) + 30 + center[1]
