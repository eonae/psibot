"""
Интерфейс для работы с задачами.
"""

# fmt: off
# isort: skip_file
from typing import Protocol
from uuid import UUID

from src.app.core.models import TranscriptionJob


class JobsRepository(Protocol):
    """
    Интерфейс для работы с задачами.
    """

    async def get_for_user_one(self, user_id: int) -> TranscriptionJob | None:  # type: ignore
        """Получает одну задачу пользователя."""

    async def get_for_user_many(self, user_id: int) -> list[TranscriptionJob]:  # type: ignore
        """Получает все задачи пользователя."""

    async def get_one(self, job_id: UUID) -> TranscriptionJob:  # type: ignore
        """Получает задачу по ID."""

    async def save(self, job: TranscriptionJob) -> TranscriptionJob:  # type: ignore
        """Сохраняет задачу."""
