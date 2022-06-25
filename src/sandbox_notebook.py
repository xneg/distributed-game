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

# %% pycharm={"name": "#%%\n"}
from viz.main import run
from ipycanvas import MultiCanvas

canvas = MultiCanvas(4, width=800, height=600)
display(canvas)
run(3, 5, canvas[0], canvas[1], canvas[2])
