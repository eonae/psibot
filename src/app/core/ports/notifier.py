from typing import Protocol

from .message_types import MessageType


class Notifier(Protocol):
    async def notify(self, user_id: int, message_type: MessageType, **params) -> None:
        ...

    async def send_result_with_confirmation(
        self, user_id: int, file: bytes, filename: str, job_id: str
    ) -> None:
        ...
