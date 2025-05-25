import logging
from uuid import UUID

from src.app.core.models import TranscriptionJob
from src.app.core.ports import JobsRepository, Notifier, MessageType
from src.app.core.services import DiarizationService

logger = logging.getLogger(__name__)


class HandleDiarizeUseCase:
    stage_name = "diarize"

    def __init__(
        self,
        jobs_repository: JobsRepository,
        diarizer: DiarizationService,
        notifier: Notifier,
    ):
        self.jobs_repository = jobs_repository
        self.diarizer = diarizer
        self.notifier = notifier

    async def execute(self, job_id: UUID, is_last_retry: bool) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.assert_is_processing()

            self.diarizer.diarize(job.files.wav, job.files.diarization)

            await self.notify_completed(job)
        except Exception as error:
            if is_last_retry:
                job.set_failed(error)
                await self.jobs_repository.save(job)
                await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify(job.user_id, MessageType.DIARIZATION_FAILED)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify(job.user_id, MessageType.DIARIZATION_COMPLETED)
