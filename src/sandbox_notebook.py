# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: .venv
# ---

# %%
# %load_ext autoreload

# %% pycharm={"name": "#%%\n"}
# %autoreload 2
from viz.main import Runner
from ipycanvas import MultiCanvas
import threading

canvas = MultiCanvas(4, width=800, height=600)
# canvas = MultiCanvas(3, width=800, height=60)

display(canvas)
runner = Runner(clients_count=2, nodes_count=3, canvas=canvas)
display(runner.get_out)

thread = threading.Thread(target=runner.run)
thread.start()

# %%
from ipycanvas import MultiCanvas
from ipywidgets import Output

canvas = MultiCanvas(4, width=800, height=60)
out = Output()

@out.capture()
def on_keyboard_event(key, shift_key, ctrl_key, meta_key):
    print("Keyboard event:", key, shift_key, ctrl_key, meta_key)

canvas[0].on_key_down(on_keyboard_event)
display(canvas)
display(out)

# %%
