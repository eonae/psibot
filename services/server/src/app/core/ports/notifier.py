"""
Интерфейс для отправки уведомлений.
"""

from typing import Protocol

from .message_types import MessageType


class Notifier(Protocol):
    """
    Интерфейс для отправки уведомлений.
    """

    async def notify(
        self,
        user_id: int,
        message_type: MessageType,
        **params,
    ) -> None:  # type: ignore
        """Отправляет уведомление пользователю."""

    async def send_greetings(self, user_id: int) -> None:
        """Отправляет клавиатуру для открытия веб-приложения."""

    async def send_result_with_confirmation(
        self,
        user_id: int,
        file: bytes,
        filename: str,
        job_id: str,
    ) -> None:  # type: ignore
        """Отправляет результат с запросом подтверждения."""
