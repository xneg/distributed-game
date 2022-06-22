from time import sleep

from IPython.core.display_functions import display
from ipycanvas import Canvas, hold_canvas


def run_animation():
    canvas = Canvas()

    display(canvas)

    # Number of steps in your animation
    steps_number = 200

    while True:
        for i in range(steps_number):
            with hold_canvas():
                # Clear the old animation step
                canvas.clear()
                canvas.fill_rect(25 + i, 25, 100, 100)

            # Animation frequency ~50Hz = 1./50. seconds
            sleep(0.02)

