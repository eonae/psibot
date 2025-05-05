# fmt: off
# isort: skip_file
from typing import Protocol
from uuid import UUID

from src.app.core.models import TranscriptionJob


class JobsRepository(Protocol):
    async def get_for_user_active(self, user_id: int) -> TranscriptionJob | None:
        ...

    async def get_for_user_many(self, user_id: int) -> list[TranscriptionJob]:
        ...

    async def get_one(self, job_id: UUID) -> TranscriptionJob:
        ...

    async def save(self, job: TranscriptionJob) -> TranscriptionJob:
        ...
