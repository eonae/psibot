import logging
from pathlib import Path

from src.app.core.models import JobStatus, TranscriptionJob
from src.app.core.ports import FileStorage, JobsRepository, Notifier, TasksScheduler
from .base import BaseStageResultHandler

logger = logging.getLogger(__name__)


class HandlePostprocessingResultUseCase(BaseStageResultHandler):
    def __init__(
        self,
        jobs_repository: JobsRepository,
        tasks_scheduler: TasksScheduler,
        notifier: Notifier,
        storage: FileStorage,
    ):
        super().__init__(jobs_repository, tasks_scheduler, notifier)
        self.storage = storage

    @property
    def expected_status(self):
        return JobStatus.POSTPROCESSING

    @property
    def next_status(self):
        return JobStatus.PENDING_CONFIRMATION

    async def schedule_next(self, job: TranscriptionJob):
        # Нет следующего шага, только смена статуса
        pass

    async def notify_failed(self, job):
        await self.notifier.notify_postprocessing_failed(job.user_id)

    async def notify_completed(self, job):
        file = self.storage.read(job.files.postprocessed)
        result_filename = Path(job.original_filename).with_suffix(".txt").name
        await self.notifier.send_result_with_confirmation(
            user_id=job.user_id,
            filename=result_filename,
            file=file,
        )
