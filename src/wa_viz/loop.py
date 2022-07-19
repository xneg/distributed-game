from typing import Awaitable
import asyncio
import pywebcanvas as pwc


class Loop:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.tasks = {}

    def add_task(self, task_name: str, task_func: Awaitable):
        pwc.log(f"Create task {task_name} {task_func}")
        self.tasks[task_name] = task_func

    def remove_task(self, task_name: str):
        del self.tasks[task_name]

    def run(self):
        async def do_loop():
            # pwc.log(f"Run loop {self} with tasks {self.tasks}")
            for func in self.tasks.values():
                try:
                    await func()
                except Exception as e:
                    pwc.log(f"task Error {e}")
            asyncio.ensure_future(do_loop())

        asyncio.ensure_future(do_loop())
        self.loop.run_forever()

    # def stop(self):
    #     from js import console
    #     console.log(str(type(self.loop)))
        # asyncio.get_event_loop().stop()
