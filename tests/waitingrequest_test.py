import pytest

from engine.contracts import RequestTimeout
from engine.utils import generator
from engine.web_server import WaitingRequest


@generator
def process_message():
    return "Ack"


@generator
def process_wait(wait_request):
    result = yield from wait_request
    return result


def caller(func):
    result = yield from func()
    print(result)


class Caller:
    def __init__(self):
        self.result = None

    @generator
    def call(self, func):
        result = yield from func()
        self.result = result


def test_0():
    c = caller(process_message)
    with pytest.raises(StopIteration):
        next(c)


def test_0_1():
    caller = Caller()
    c = caller.call(process_message)
    with pytest.raises(StopIteration):
        next(c)
    assert caller.result == "Ack"


def test_waiting_request_triggers():
    wait_request = WaitingRequest()
    caller = Caller()
    c = caller.call(wait_request.wait)

    for i in range(0, 5):
        next(c)

    wait_request.trigger("Ok!")

    with pytest.raises(StopIteration):
        next(c)

    assert caller.result == "Ok!"


def test_waiting_request_timeouts():
    wait_request = WaitingRequest(timeout=3)
    caller = Caller()
    c = caller.call(wait_request.wait)

    for i in range(0, 3):
        next(c)

    with pytest.raises(StopIteration):
        next(c)

    assert isinstance(caller.result, RequestTimeout)
