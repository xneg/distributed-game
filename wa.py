from pyodide.ffi import create_proxy
from js import console, window
import pywebcanvas as pwc

from engine.node import Node
from wa_viz.loop import Loop
from wa_viz.main import Runner

from pyscript import document

pwc.disable_logging(True)
canvas = pwc.Canvas(800, 600)
runner = Runner(canvas)
loop = Loop()

# async def on_update():
#     await runner.run()


def run(*args, **kwargs):
    run_button.disabled = True
    text = document.getElementById("test-input").value
    exec(text, globals(), globals())
    clients_count = document.getElementById("clients-count").value
    nodes_count = document.getElementById("nodes-count").value
    runner.setup(
        node_type=Node.__subclasses__()[-1],
        clients_count=int(clients_count),
        nodes_count=int(nodes_count),
    )
    pwc.add_event_handler("mousemove", runner.handle_mouse_move)
    loop.add_task("on_update", runner.run)
    loop.run()


def pause(*args, **kwargs):
    console.log("PAUSE!")
    runner.switch_pause()


def clear(*args, **kwargs):
    # from js import console
    # console.warn("CLEAR!")
    loop.remove_task("on_update")
    runner.clear()
    run_button.disabled = False


# n_clusters = pn.widgets.IntSlider(name='n_clusters', start=1, end=5, value=3)
# show(n_clusters, 'n-widget')

run_button = document.getElementById("run-button")
run_button.addEventListener("click", create_proxy(run))

pause_button = document.getElementById("pause-button")
pause_button.addEventListener("click", create_proxy(pause))

clear_button = document.getElementById("clear-button")
clear_button.addEventListener("click", create_proxy(clear))

import wa_viz.single_client_versioned_majority

file_path = wa_viz.single_client_versioned_majority.__file__
with open(file_path) as example_code_module:
    example_code = example_code_module.read()
document.getElementById("example-code").innerText = example_code
