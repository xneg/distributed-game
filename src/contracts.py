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


def make_timer():
    registry = []

    def reg(interval):
        def inner(func):
            registry.append((func, interval))
            return func

        reg.all = registry
        return inner

    return reg