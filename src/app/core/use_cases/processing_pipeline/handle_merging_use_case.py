import logging
from uuid import UUID

from src.app.core.models import TranscriptionJob
from src.app.core.ports.jobs_repository import JobsRepository
from src.app.core.ports.notifier import Notifier
from src.app.core.services.merging_service import MergingService

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

    async def execute(self, job_id: UUID) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.assert_is_processing()

            self.merger.merge(
                job.files.diarization,
                job.files.transcription,
                job.files.merged,
            )

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            job.set_failed(error)
            await self.jobs_repository.save(job)
            await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_transcribing_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_transcribing_completed(job.user_id)
