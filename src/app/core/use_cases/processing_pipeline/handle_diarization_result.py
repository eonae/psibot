import logging

from src.app.core.models import JobStatus, TranscriptionJob
from .base import BaseStageResultHandler

logger = logging.getLogger(__name__)


class HandleDiarizationResultUseCase(BaseStageResultHandler):
    @property
    def expected_status(self):
        return JobStatus.DIARIZING

    @property
    def next_status(self):
        return JobStatus.TRANSCRIBING

    async def schedule_next(self, job: TranscriptionJob):
        self.tasks_scheduler.schedule(
            task_name="transcribe",
            job_id=job.id,
            wav_filename=str(job.files.wav),
            target_filename=str(job.files.transcription),
        )

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_diarization_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_diarization_completed(job.user_id)
