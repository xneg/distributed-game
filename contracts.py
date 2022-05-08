from dataclasses import dataclass
from enum import Enum
from typing import Any


class RequestType(Enum):
    Read = 1,
    Write = 2


@dataclass(frozen=True)
class ClientRequest:
    client: Any
    type: RequestType
    value: int = None


@dataclass(frozen=True)
class ClientResponse:
    client: Any
    type: RequestType
    value: Any