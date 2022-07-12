import pywebcanvas as pwc

from wa_viz.circle import Circle

NODES_BACKGROUND = "#FED9B7"
GATEWAY_BACKGROUND = "#7FD6CB"  # "#FDFCDC"
CLIENTS_BACKGROUND = "#BEE9D4"

CLIENT_COLOR = "#FED9B7"  # "#00AFB9"
GATEWAY_COLOR = "#00AFB9"
NODE_COLOR = "#F07167"
SIGNAL_COLOR = "#0081A7"  # "#03B5AA"


def draw_red_rectangle(canvas):
    canvas.render(pwc.Rect(100, 200, 15, 100, color="red"))


def draw_objects_count(canvas, count):
    canvas.render(pwc.Text(f"Objects count {count}", 350, 50, size=30, color="black"))


def draw_background(canvas):
    canvas.render(
        Circle(canvas.width // 2, canvas.height // 4 + 30, 120, NODES_BACKGROUND)
    )
    canvas.render(
        pwc.Rect(0, canvas.height * 3 // 4 - 100, canvas.width, 100, GATEWAY_BACKGROUND)
    )
