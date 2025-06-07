"""
Обработчик загрузки аудио-файла.
"""

import logging
from uuid import UUID

from src.app.core.models import TranscriptionJob
from src.app.core.models.transcription_job import SourceType
from src.app.core.ports import (
    FileLoader,
    FileStorage,
    JobsRepository,
    Notifier,
    MessageType,
)

logger = logging.getLogger(__name__)


class HandleDownloadUseCase:
    """
    Обработчик загрузки аудио-файла.
    """

    stage_name = "download"

    def __init__(
        self,
        jobs_repository: JobsRepository,
        notifier: Notifier,
        storage: FileStorage,
        loaders: list[FileLoader],
    ):
        self.jobs_repository = jobs_repository
        self.notifier = notifier
        self.storage = storage
        self.loaders = loaders

    async def execute(self, job_id: UUID, is_last_retry: bool) -> None:
        """
        Выполняет загрузку аудио-файла.
        """

        job = await self.jobs_repository.get_one(job_id)

        try:
            if job.source.type not in [
                SourceType.UPLOAD_URL,
                SourceType.TELEGRAM_FILE_ID,
            ]:
                raise ValueError("Invalid source type")

            loader = next(
                (x for x in self.loaders if x.is_valid_file_id(job.source.value)),
            )

            if not loader:
                raise ValueError("No loader found for URL")

            content, filename = loader.load(job.source.value)

            job.to_processing(filename)

            self.storage.save(content, job.paths.original)
            logger.info("✅ Audio file downloaded and saved: %s", job.paths.original)

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            if is_last_retry:
                job.set_failed(error)
                await self.jobs_repository.save(job)
                await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        """
        Уведомляет пользователя о неудачной загрузке аудио-файла.
        """

        await self.notifier.notify(job.user_id, MessageType.DOWNLOAD_FAILED)

    async def notify_completed(self, job: TranscriptionJob):
        """
        Уведомляет пользователя о успешной загрузке аудио-файла.
        """

        await self.notifier.notify(job.user_id, MessageType.DOWNLOAD_COMPLETED)
