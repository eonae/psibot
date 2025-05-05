import logging

from src.app.core.models import JobStatus, TranscriptionJob
from .base import BaseStageResultHandler

logger = logging.getLogger(__name__)


class HandleTranscriptionResultUseCase(BaseStageResultHandler):
    @property
    def expected_status(self):
        return JobStatus.TRANSCRIBING

    @property
    def next_status(self):
        return JobStatus.MERGING

    async def schedule_next(self, job: TranscriptionJob):
        self.tasks_scheduler.schedule(
            task_name="merge",
            job_id=job.id,
            diarization_filename=str(job.files.diarization),
            transcription_filename=str(job.files.transcription),
            target_filename=str(job.files.merged),
        )

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_transcribing_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_transcribing_completed(job.user_id)
