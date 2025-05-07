import logging
from uuid import UUID

from anyio import Path

from src.app.core.models import TranscriptionJob
from src.app.core.ports.file_storage import FileStorage
from src.app.core.ports.jobs_repository import JobsRepository
from src.app.core.ports.notifier import Notifier
from src.app.core.services.postprocessing_service import PostprocessingService

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

    async def execute(self, job_id: UUID) -> None:
        job = await self.jobs_repository.get_one(job_id)

        try:
            job.to_confirmation()

            self.postprocessor.postprocess(job.files.merged, job.files.postprocessed)

            await self.jobs_repository.save(job)
            await self.notify_completed(job)
        except Exception as error:
            job.set_failed(error)
            await self.jobs_repository.save(job)
            await self.notify_failed(job)

            raise error

    async def notify_failed(self, job: TranscriptionJob):
        await self.notifier.notify_postprocessing_failed(job.user_id)

    async def notify_completed(self, job: TranscriptionJob):
        file = self.storage.read(job.files.postprocessed)
        result_filename = Path(job.original_filename).with_suffix(".txt").name

        await self.notifier.send_result_with_confirmation(
            user_id=job.user_id,
            filename=result_filename,
            file=file,
        )
