import itertools

import pytest

from engine.contracts import RequestTimeout
from engine.utils import generator
from engine.web_server import WaitingRequest, ParallelTasks


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


# def test_0():
#     c = caller(process_message)
#     with pytest.raises(StopIteration):
#         next(c)


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

    assert caller.result == RequestTimeout()


def test_parallel_tasks_wait_any_count():
    wait_requests = []
    parallel_tasks = ParallelTasks()
    caller = Caller()

    for i in range(0, 4):
        request = WaitingRequest()
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


def test_parallel_tasks_wait_any_by_timeout():
    wait_requests = []
    parallel_tasks = ParallelTasks()
    caller = Caller()

    for i in range(0, 4):
        request = WaitingRequest(timeout=3 + i)
        wait_requests.append(request)
        parallel_tasks.add(request)

    c = caller.call(parallel_tasks.wait_any(min_count=2))

    for i in range(0, 4):
        next(c)

    with pytest.raises(StopIteration):
        next(c)

    assert caller.result == [RequestTimeout(), RequestTimeout(), None, None]


def test_xx():
    caller = Caller()
    parallel_tasks = ParallelTasks()

    parallel_tasks.add(WaitingRequest(timeout=2))
    parallel_tasks.add(WaitingRequest(timeout=2))
    c = caller.call(parallel_tasks.wait_all())

    for i in range(0, 4):
        next(c)

    # with pytest.raises(StopIteration):
    #     next(c)


def test_parallel_tasks_wait_all():
    wait_requests = []
    parallel_tasks = ParallelTasks()
    caller = Caller()

    for i in range(0, 4):
        request = WaitingRequest(timeout=3 + i)
        wait_requests.append(request)
        parallel_tasks.add(request)

    c = caller.call(parallel_tasks.wait_all())

    for i in range(0, 15):
        next(c)
    #
    # with pytest.raises(StopIteration):
    #     next(c)
    #
    # assert caller.result == [RequestTimeout(), RequestTimeout(), None, None]