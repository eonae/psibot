import logging

from src.app.core.models import JobStatus, TranscriptionJob
from .base import BaseStageResultHandler

logger = logging.getLogger(__name__)


class HandleConvertResultUseCase(BaseStageResultHandler):
    @property
    def expected_status(self):
        return JobStatus.CONVERTING

    @property
    def next_status(self):
        return JobStatus.DIARIZING

    async def schedule_next(self, job: TranscriptionJob):
        self.tasks_scheduler.schedule(
            task_name="diarize",
            job_id=job.id,
            wav_filename=str(job.files.wav),
            target_filename=str(job.files.diarization),
        )

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_convert_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_convert_completed(job.user_id)
