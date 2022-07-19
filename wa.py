import pywebcanvas as pwc

from engine.node import Node
# from pyscript.pyscript import Element
from wa_viz.main import Runner
from pyodide import create_proxy

canvas = pwc.Canvas(800, 600)
runner = Runner(canvas)
loop = pwc.Loop()

# clicks_count = 0
#
#
# def on_click(e):
#     global clicks_count
#     global text
#     clicks_count = clicks_count + 1
#     text.text = str(clicks_count)


async def on_update():
    await runner.run()


def my_function(*args, **kwargs):
    text = Element('test-input').element.value
    # console.warn(text)
    exec(text, globals(), globals())
    # for k, v in list(globals().items()):
    #     console.warn(k + " " + str(type(v)))
        # if issubclass(type(v), Node):
    # console.warn(str(type(Node.__subclasses__()[-1])))

    # Element('test-output').element.innerText = str(Node.__subclasses__()[-1])
    # runner.setup(node_type=SingleClientVersionedMajority)
    runner.setup(node_type=Node.__subclasses__()[-1])
    pwc.add_event_handler("mousemove", runner.handle_mouse_move)
    loop.add_task("on_update", on_update)
    loop.run()
# n_clusters = pn.widgets.IntSlider(name='n_clusters', start=1, end=5, value=3)
# show(n_clusters, 'n-widget')

button = document.getElementById("submit-button")
button.addEventListener("click", create_proxy(my_function))

import wa_viz.single_client_versioned_majority
file_path = wa_viz.single_client_versioned_majority.__file__
with open(file_path) as example_code_module:
    example_code = example_code_module.read()
Element('example-code').element.innerText = example_code