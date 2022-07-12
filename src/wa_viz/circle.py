import math
from colour import Color


class Circle:
    def __init__(self, x, y, radius, color="black", type_="fill"):
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.type_ = type_
    
    def render(self, canvas):
        ctx = canvas.ctx()

        hex_color = Color(self.color).hex 
        ctx.fillStyle = hex_color

        args = (self.x, self.y, self.radius)

        ctx.beginPath()
        ctx.arc(*args, 0, 2 * math.pi)
        ctx.fillStyle = self.color
        ctx.fill()
        # context.lineWidth = 5;
        # context.strokeStyle = '#003300';
        # context.stroke();

        # if self.type_ == "fill":
        #     ctx.fillCircle(*args)
        # elif self.type_ == "stroke":
        #     ctx.strokeCircle(*args)
        # elif self.type_ == "clear":
        #     ctx.clearCircle(*args)
