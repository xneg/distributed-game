# NODES_BACKGROUND = "#FFDAC6"
# GATEWAY_BACKGROUND = "#FDB863"
# CLIENTS_BACKGROUND = "#BABD8D"
#
# CLIENT_COLOR = "#7C6A0A"
# GATEWAY_COLOR = "#7C6A0A"
# NODE_COLOR = "#FA9500"
# SIGNAL_COLOR = "#EB6424" # "#03B5AA"

NODES_BACKGROUND = "#FED9B7"
GATEWAY_BACKGROUND = "#7FD6CB"  # "#FDFCDC"
CLIENTS_BACKGROUND = "#BEE9D4"

CLIENT_COLOR = "#FED9B7" # "#00AFB9"
GATEWAY_COLOR = "#00AFB9"
NODE_COLOR = "#F07167"
SIGNAL_COLOR = "#0081A7"  # "#03B5AA"


def draw_background(canvas):
    canvas.fill_style = NODES_BACKGROUND
    canvas.fill_circle(canvas.width // 2, canvas.height // 4 + 30, 120)
    # canvas.fill_rect(0, 0, canvas.width, canvas.height * 4 // 3)
    # canvas.fill_style = CLIENTS_BACKGROUND
    # canvas.fill_rect(0, canvas.height * 3 // 4, canvas.width, canvas.height // 2)
    canvas.fill_style = GATEWAY_BACKGROUND
    canvas.fill_rect(0, canvas.height * 3 // 4 - 100, canvas.width, 100)
