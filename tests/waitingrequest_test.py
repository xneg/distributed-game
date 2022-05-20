import pytest

from engine.utils import generator


@generator
def process_message():
    return "Ack"


def caller(func):
    result = yield from func()
    print(result)


def test_0():
    c = caller(process_message)
    with pytest.raises(StopIteration):
        next(c)
