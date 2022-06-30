from viz.utils import CLIENT_COLOR


class ClientViz:
    def __init__(self, client, clients_count, canvas):
        self.client = client
        self.canvas = canvas
        self.x = 0
        self.y = 0

        index = int(self.client.id.replace("client_", "")) - 1
        self._set_position(clients_count, index)

    def move(self, progress):
        pass

    def draw(self):
        self.canvas.fill_style = CLIENT_COLOR
        self.canvas.fill_rect(self.x - 50, self.y - 20, 100, 40)
        self.canvas.fill_style = "black"
        self.canvas.font = "20px serif"
        self.canvas.fill_text(self.client.id, self.x - 30, self.y + 10)
        self.canvas.fill_text(self.client.state, self.x - 20, self.y + 50)

    def set_hovered(self, x, y):
        pass

    def click(self, x, y):
        pass

    @property
    def coordinates(self):
        return self.x, self.y

    def _set_position(self, clients_count, index):
        gap = (self.canvas.width - clients_count * 100) // (clients_count + 1)
        self.x = gap + (100 + gap) * index + 50
        self.y = self.canvas.height * 5 // 6 + 20
