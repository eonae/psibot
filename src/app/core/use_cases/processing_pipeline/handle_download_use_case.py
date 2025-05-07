import logging
from uuid import UUID

from src.app.core.models import TranscriptionJob
from src.app.core.ports import FileLoader, FileStorage, JobsRepository, Notifier

logger = logging.getLogger(__name__)


class HandleDownloadUseCase:
    stage_name = "download"

    def __init__(
        self,
        jobs_repository: JobsRepository,
        notifier: Notifier,
        storage: FileStorage,
        loader: FileLoader,
    ):
        self.jobs_repository = jobs_repository
        self.notifier = notifier
        self.storage = storage
        self.loader = loader

    async def execute(self, job_id: UUID) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.to_processing()

            content = self.loader.load(job.file_id)
            self.storage.save(content, job.files.original)
            logger.info("✅ Audio file downloaded and saved: %s", job.files.original)

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            job.set_failed(error)
            await self.jobs_repository.save(job)
            await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_download_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_download_completed(job.user_id)
