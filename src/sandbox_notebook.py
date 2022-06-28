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

# %%
from dataclasses import dataclass
from operator import attrgetter

from engine.contracts import (
    ClientReadRequest,
    ClientWriteRequest,
    ClientReadResponse,
    ResponseType,
    ClientWriteResponse,
)
from engine.node import Node
from engine.web_server import WebServer


@dataclass
class ReadRequest:
    pass


@dataclass
class GetVersionRequest:
    pass


@dataclass
class ReadResponse:
    value: int
    version: int


@dataclass
class VersionResponse:
    version: int
    id: int


@dataclass
class WriteRequest:
    value: int
    version: int


# noinspection PyTypeChecker
class SingleClientVersionedMajority(Node):
    @property
    def write_quorum(self):
        return len(self.other_nodes) // 2

    @property
    def read_quorum(self):
        return len(self.other_nodes) // 2

    @WebServer.endpoint(message_type=ClientReadRequest)
    def process_read_request(self, request):
        responses = yield from self.wait_for_responses(
            request=ReadRequest(),
            check_response=lambda x: isinstance(x, ReadResponse),
            count=self.read_quorum,
        )

        value, version = self.get_value()
        responses.append(ReadResponse(value=value, version=version))

        result = max(responses, key=attrgetter("version")).value
        return ClientReadResponse(result=ResponseType.Success, value=result)

    @WebServer.endpoint(message_type=ClientWriteRequest)
    def process_write_request(self, request: ClientWriteRequest):
        responses = yield from self.wait_for_responses(
            request=GetVersionRequest(),
            check_response=lambda x: isinstance(x, VersionResponse),
            count=self.write_quorum,
        )

        version = max(responses, key=attrgetter("version")).version
        version = max(version, self.get_version()) + 1
        self.storage["x"] = (request.value, version)

        yield from self.wait_for_responses(
            request=WriteRequest(value=request.value, version=version),
            check_response=lambda x: x == "Ack",
            count=len(responses)
        )

        return ClientWriteResponse(result=ResponseType.Success)

    @WebServer.endpoint(message_type=ReadRequest)
    def read_request(self, _):
        value, version = self.get_value()
        return ReadResponse(value=value, version=version)

    def get_value(self):
        value, version = (
            (self.storage["x"][0], self.storage["x"][1])
            if "x" in self.storage
            else ("N", 0)
        )
        return value, version

    @WebServer.endpoint(message_type=GetVersionRequest)
    def version_request(self, _):
        version = self.get_version()
        return VersionResponse(version=version, id=self.id)

    def get_version(self):
        version = self.storage["x"][1] if "x" in self.storage else 0
        return version

    @WebServer.endpoint(message_type=WriteRequest)
    def write_request(self, request: WriteRequest):
        self.storage["x"] = (request.value, request.version)
        # TODO: without return "Ack" (or anything else) wait_all doesn't work
        return "Ack"


# %% pycharm={"name": "#%%\n"}
# %autoreload 2
from viz.main import Runner
from ipycanvas import MultiCanvas, MultiRoughCanvas
import threading

canvas = MultiCanvas(4, width=800, height=600)
# canvas = MultiRoughCanvas(4, width=800, height=600)

display(canvas)
runner = Runner(clients_count=2, nodes_count=3, canvas=canvas, node_type=SingleClientVersionedMajority)
display(runner.get_out)

# runner.run()
thread = threading.Thread(target=runner.run)
thread.start()

# %%
from ipywidgets import Output
from ipycanvas import RoughCanvas, MultiRoughCanvas

out = Output()
multiCanvas = MultiRoughCanvas(4, width=80, height=60)
# canvas = RoughCanvas(width=80, height=60)
canvas = multiCanvas[0]


@out.capture()
def on_keyboard_event(key, shift_key, ctrl_key, meta_key):
    print("Keyboard event:", key, shift_key, ctrl_key, meta_key)

# canvas._canvases[-1].on_key_down(on_keyboard_event)
canvas.on_key_down(on_keyboard_event)

display(canvas)
display(out)
