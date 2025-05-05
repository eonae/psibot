import logging

from src.app.core.models import JobStatus, TranscriptionJob
from .base import BaseStageResultHandler

logger = logging.getLogger(__name__)


class HandleMergeResultUseCase(BaseStageResultHandler):
    @property
    def expected_status(self):
        return JobStatus.MERGING

    @property
    def next_status(self):
        return JobStatus.POSTPROCESSING

    async def schedule_next(self, job: TranscriptionJob):
        self.tasks_scheduler.schedule(
            task_name="postprocess",
            job_id=job.id,
            source_filename=str(job.files.merged),
            target_filename=str(job.files.postprocessed),
        )

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_merge_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        await self.notifier.notify_merge_completed(job.user_id)
