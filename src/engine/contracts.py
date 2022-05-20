from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResponseType(Enum):
    Success = (1,)
    Fail = 2


@dataclass(frozen=True)
class ClientWriteRequest:
    value: int


@dataclass(frozen=True)
class ClientWriteResponse:
    result: ResponseType


@dataclass(frozen=True)
class ClientReadRequest:
    pass


@dataclass(frozen=True)
class ClientReadResponse:
    result: ResponseType
    value: int


@dataclass(frozen=True)
class LeaderNotification:
    id: Any


@dataclass
class RequestTimeout:
    pass
