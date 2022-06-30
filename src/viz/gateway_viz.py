from viz.utils import GATEWAY_COLOR


class GatewayViz:
    def __init__(self, canvas):
        self.canvas = canvas

        self.x = self.canvas.width // 2
        self.y = self.canvas.height * 3 // 4 - 40

    def move(self, progress):
        pass

    def draw(self):
        self.canvas.fill_style = GATEWAY_COLOR
        self.canvas.fill_rect(self.x - 50, self.y - 30, 100, 60)
        self.canvas.fill_style = "black"
        self.canvas.font = "20px serif"
        self.canvas.fill_text("Gateway", self.x - 35, self.y + 5)

    @property
    def coordinates(self):
        return self.x, self.y