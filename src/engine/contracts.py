import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class RequestType(Enum):
    Read = 1,
    Write = 2


class ResponseType(Enum):
    Success = 1,
    Fail = 2


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


class MessageResponse:
    def __init__(self, message_packet: MessagePacket, response):
        self._id = message_packet.id
        self._response = response

    @property
    def id(self):
        return self._id

    @property
    def response(self):
        return self._response
