import pywebcanvas as pwc

from wa_viz.main import Runner

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

runner.setup()
pwc.add_event_handler("mousemove", runner.handle_mouse_move)
loop.add_task("on_update", on_update)
loop.run()
