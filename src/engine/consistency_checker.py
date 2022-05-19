import logging

from engine.contracts import RequestType, ClientRequest
from engine.singleton import Singleton
from engine.timer import Timer


class ConsistencyChecker(metaclass=Singleton):
    def __init__(self):
        self._client_lines = {}
        self._timer = Timer()
        logging.info(f"Consistency checker created at {self._timer.current_epoch()}")

    def add_request(self, client_id, request):
        if client_id not in self._client_lines:
            self._client_lines[client_id] = []
        self._client_lines[client_id].append((self._timer.current_epoch(), request))

    def add_response(self, client_id, response):
        if client_id not in self._client_lines:
            self._client_lines[client_id] = []
        self._client_lines[client_id].append((self._timer.current_epoch(), response))

    def process(self):
        line = str(self._timer.current_epoch()) + " "
        for client in self._client_lines:
            (time, event) = self._client_lines[client][-1]
            if time != self._timer.current_epoch():
                line = line + ("|" if isinstance(event, ClientRequest) else " ")
            else:
                if event.type == RequestType.Read:
                    line = (
                        line + "R" + str(event.value if event.value is not None else "")
                    )
                else:
                    line = line + "W" + str(event.value)[0]
            line = line + " " * (4 - len(line) % 4)
        print(line)
