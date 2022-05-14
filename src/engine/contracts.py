import inspect
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class RequestType(Enum):
    Read = 1,
    Write = 2


@dataclass(frozen=True)
class ClientRequest:
    type: RequestType
    value: int = None
    id: UUID = field(default_factory=uuid.uuid4, init=False)


@dataclass(frozen=True)
class ClientResponse:
    type: RequestType
    value: Any
    id: UUID


class MessagePacket:
    def __init__(self, message):
        self._message = message
        self._id = uuid.uuid4()

    @property
    def message(self):
        return self._message

    @property
    def id(self):
        return self._id


class MessageAck:
    def __init__(self, message_packet: MessagePacket):
        self._id = message_packet.id

    @property
    def id(self):
        return self._id


def make_timer():
    registry = []

    def reg(interval):
        def inner(func):
            registry.append((func, interval))
            return func

        reg.all = registry
        return inner

    reg.all = reg.all if hasattr(reg, 'all') else []

    return reg


def generator(func):
    def wrapper(*a, **ka):
        if not inspect.isgeneratorfunction(func):
            func(*a, **ka)
            yield
        else:
            yield from func(*a, **ka)
    return wrapper
