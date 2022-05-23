import itertools

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
        result = yield from func
        self.result = result


def test_0():
    c = caller(process_message)
    with pytest.raises(StopIteration):
        next(c)


def test_0_1():
    caller = Caller()
    c = caller.call(process_message())
    with pytest.raises(StopIteration):
        next(c)
    assert caller.result == "Ack"


def test_waiting_request_triggers():
    wait_request = WaitingRequest()
    caller = Caller()
    c = caller.call(wait_request.wait())

    for i in range(0, 5):
        next(c)

    wait_request.trigger("Ok!")

    with pytest.raises(StopIteration):
        next(c)

    assert caller.result == "Ok!"


def test_waiting_request_timeouts():
    wait_request = WaitingRequest(timeout=3)
    caller = Caller()
    c = caller.call(wait_request.wait())

    for i in range(0, 3):
        next(c)

    with pytest.raises(StopIteration):
        next(c)

    assert isinstance(caller.result, RequestTimeout)


class TestWait:
    def __init__(self, name, timeout=-1):
        self.name = name
        self._trigger = False
        self._response = None
        self._timeout = timeout
        self._timer = 0
        self.result = None

    def trigger(self, response):
        self._trigger = True
        self._response = response

    def wait(self):
        while not self._trigger and self._timer != self._timeout:
            self._timer = self._timer + 1
            yield False
        self.result = RequestTimeout() if self._timer == self._timeout else self._response
        return self.result


def check(count, tuple):
    return sum(x is None for x in tuple) < count


def test_xx():
    wait_request_a = TestWait(name="a")
    wait_request_b = TestWait(name="b")
    wait_request_c = TestWait(name="c")
    z = itertools.zip_longest(
        wait_request_a.wait(),
        wait_request_b.wait(),
        wait_request_c.wait())

    t = itertools.takewhile(lambda x: check(2, x), z)

    caller = Caller()
    c = caller.call(t)

    for i in range(0, 3):
        next(c)

    wait_request_a.trigger(response="Ok")

    for i in range(0, 3):
        next(c)

    wait_request_b.trigger(response="Ok")
    with pytest.raises(StopIteration):
        next(c)
    print(f"a: {wait_request_a.result} b: {wait_request_b.result} c: {wait_request_c.result}")
    # assert caller.result is not None


class ParallelTasks:
    def __init__(self):
        self._requests = []

    def add(self, request):
        self._requests.append(request)

    def wait_any(self, min_count):
        waits = [r.wait() for r in self._requests]
        z = itertools.zip_longest(*waits)
        yield from itertools.takewhile(lambda x: self.__check(min_count, x), z)
        return [r.result for r in self._requests]

    def __check(self, count, tuple):
        r = sum(x is None for x in tuple) < count
        if r:
            return True
        return False


def test_yy():
    letters = ['a', 'b', 'c', 'd']
    wait_requests = []
    parallel_tasks = ParallelTasks()
    caller = Caller()

    for l in letters:
        request = TestWait(name=l)
        wait_requests.append(request)
        parallel_tasks.add(request)

    c = caller.call(parallel_tasks.wait_any(min_count=2))

    for i in range(0, 5):
        next(c)

    wait_requests[0].trigger("Ok!")

    for i in range(0, 3):
        next(c)

    wait_requests[2].trigger("Ok!")

    with pytest.raises(StopIteration):
        next(c)

    assert caller.result == ['Ok!', None, 'Ok!', None]
