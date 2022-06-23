import math


def draw_background(canvas):
    canvas.fill_style = "#CCB7AE"
    canvas.fill_rect(0, 0, canvas.width, canvas.height * 4 // 3)
    canvas.fill_style = "#706677"
    canvas.fill_rect(0, canvas.height * 3 // 4, canvas.width, canvas.height // 2)
    canvas.fill_style = "#A6808C"
    canvas.fill_rect(0, canvas.height * 3 // 4 - 100, canvas.width, 100)


def draw_client(canvas, index, client_id, clients_count):
    gap = (canvas.width - clients_count * 100) // (clients_count + 1)
    x = gap + (100 + gap) * index
    y = canvas.height * 5 // 6
    canvas.fill_style = "#565264"
    canvas.fill_rect(x, y, 100, 40)
    canvas.fill_style = "black"
    canvas.font = "20px serif"
    canvas.fill_text(client_id, x + 20, y + 30)
    return x + 50, y + 20


def draw_node(canvas, index, node_id, nodes_count):
    r = 120
    t = math.pi * 2 / nodes_count * index
    x = r * math.cos(t - math.pi / 2)
    y = r * math.sin(t - math.pi / 2)
    canvas.fill_style = "#565264"
    canvas.fill_circle(x, y + 30, 30)
    canvas.fill_style = "black"
    canvas.font = "32px serif"
    canvas.fill_text(node_id, x - 7, y + 37)
    return x, y + 30
