import logging

from engine.contracts import (
    ClientReadRequest,
    ClientWriteRequest,
    ClientReadResponse,
    ClientWriteResponse,
)
from engine.singleton import Singleton
from engine.timer import Timer


class ConsistencyChecker(metaclass=Singleton):
    def __init__(self):
        self._client_lines = {}
        self._timer = Timer()
        logging.info(f"Consistency checker created at {self._timer.current_epoch()}")

    def add_event(self, client_id, event):
        if client_id not in self._client_lines:
            self._client_lines[client_id] = []
        self._client_lines[client_id].append((self._timer.current_epoch(), event))

    def process(self):
        pass
        # line = str(self._timer.current_epoch()) + " "
        # for client in self._client_lines:
        #     (time, event) = self._client_lines[client][-1]
        #     if time != self._timer.current_epoch():
        #         line = line + (
        #             "|"
        #             if isinstance(event, ClientReadRequest)
        #             or isinstance(event, ClientWriteRequest)
        #             else " "
        #         )
        #     else:
        #         if isinstance(event, ClientReadRequest):
        #             line = line + "R"
        #         elif isinstance(event, ClientReadResponse):
        #             line = line + "R" + str(event.value)
        #         elif isinstance(event, ClientWriteRequest):
        #             line = line + "W" + str(event.value)
        #         elif isinstance(event, ClientWriteResponse):
        #             line = line + "W+"
        #     line = line + " " * (4 - len(line) % 4)
        # print(line)
