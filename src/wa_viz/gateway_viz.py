from wa_viz.utils import GATEWAY_COLOR
import pywebcanvas as pwc


class GatewayViz:
    def __init__(self, canvas):
        self.hovered = False
        self.canvas = canvas

        self.x = self.canvas.width // 2
        self.y = self.canvas.height * 3 // 4 - 40

    def move(self, progress):
        pass

    def draw(self):
        self.canvas.render(pwc.Rect(self.x - 50, self.y - 30, 100, 60, GATEWAY_COLOR))
        self.canvas.render(pwc.Text("Gateway", self.x - 35, self.y + 5))
        # self.canvas.font = "20px serif"
        if self.hovered:
            self.canvas.render(pwc.Text("Hovered", self.x - 35, self.y + 40))

    def set_hovered(self, x, y):
        self.hovered = (self.x - 50 <= x <= self.x + 50) \
                       and (self.y - 30 <= y <= self.y + 30)

    def click(self, x, y):
        pass

    @property
    def coordinates(self):
        return self.x, self.y