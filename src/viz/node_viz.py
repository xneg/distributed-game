import math

from viz.utils import NODE_COLOR


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
        self.canvas.fill_style = NODE_COLOR
        self.canvas.fill_circle(self.x, self.y, 30)
        self.canvas.fill_style = "black"
        self.canvas.font = "32px serif"
        self.canvas.fill_text(self.node.id, self.x - 7, self.y + 7)
        self.canvas.font = "24px serif"
        self.canvas.fill_text(str(self.node.storage), self.x - 15, self.y + 50)

    @property
    def coordinates(self):
        return self.x, self.y

    def _set_position(self, nodes_count, index):
        center = (self.canvas.width // 2, self.canvas.height // 4)
        r = 120
        t = math.pi * 2 / nodes_count * index
        self.x = r * math.cos(t - math.pi / 2) + center[0]
        self.y = r * math.sin(t - math.pi / 2) + 30 + center[1]
