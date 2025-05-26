import logging
from uuid import UUID

from src.app.core.models import TranscriptionJob
from src.app.core.ports import JobsRepository, Notifier, MessageType
from src.app.core.services import MergingService

logger = logging.getLogger(__name__)


class HandleMergingUseCase:
    stage_name = "merge"

    def __init__(
        self,
        jobs_repository: JobsRepository,
        merger: MergingService,
        notifier: Notifier,
    ):
        self.jobs_repository = jobs_repository
        self.merger = merger
        self.notifier = notifier

    async def execute(self, job_id: UUID, is_last_retry: bool) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.to_postprocessing()

            self.merger.merge(
                transcription_filename=job.files.transcription,
                diarization_filename=job.files.diarization,
                target_filename=job.files.merged,
            )

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            # Проверяем, является ли это последней попыткой
            if is_last_retry:
                job.set_failed(error)
                await self.jobs_repository.save(job)
                await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify(job.user_id, MessageType.MERGE_FAILED)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify(job.user_id, MessageType.MERGE_COMPLETED)
