import logging
from uuid import UUID
from pathlib import Path

from src.app.core.models import TranscriptionJob
from src.app.core.ports import FileStorage, JobsRepository, Notifier
from src.app.core.services import PostprocessingService
from src.app.core.ports import MessageType

logger = logging.getLogger(__name__)


class HandlePostprocessingUseCase:
    stage_name = "postprocessing"

    def __init__(
        self,
        jobs_repository: JobsRepository,
        postprocessor: PostprocessingService,
        storage: FileStorage,
        notifier: Notifier,
    ):
        self.jobs_repository = jobs_repository
        self.postprocessor = postprocessor
        self.storage = storage
        self.notifier = notifier

    async def execute(self, job_id: UUID, is_last_retry: bool) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.to_confirmation()

            self.postprocessor.postprocess(job.paths.merged, job.paths.postprocessed)

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            if is_last_retry:
                job.set_failed(error)
                await self.jobs_repository.save(job)
                await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify(job.user_id, MessageType.POSTPROCESSING_FAILED)

    async def notify_completed(self, job: TranscriptionJob):
        file = self.storage.read(job.paths.postprocessed)
        if not job.original_filename:
            raise ValueError("Original filename is not set")

        result_filename = Path(job.original_filename).with_suffix(".txt").name

        await self.notifier.send_result_with_confirmation(
            user_id=job.user_id,
            filename=result_filename,
            file=file,
            job_id=str(job.id),
        )
