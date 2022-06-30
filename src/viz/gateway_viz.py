from viz.utils import GATEWAY_COLOR


class GatewayViz:
    def __init__(self, canvas):
        self.hovered = False
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
        if self.hovered:
            self.canvas.fill_text("Hovered", self.x - 35, self.y + 40)

    def set_hovered(self, x, y):
        self.hovered = (self.x - 50 <= x <= self.x + 50) \
                       and (self.y - 30 <= y <= self.y + 30)

    def click(self, x, y):
        pass

    @property
    def coordinates(self):
        return self.x, self.y