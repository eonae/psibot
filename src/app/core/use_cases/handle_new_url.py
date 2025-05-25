import logging
from urllib.parse import urlparse

from src.app.core.models import TranscriptionJob
from src.app.core.ports import JobsRepository, Notifier, PipelineRunner, MessageType

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024


class HandleNewUrlUseCase:
    def __init__(
        self,
        jobs: JobsRepository,
        notifier: Notifier,
        pipeline_runner: PipelineRunner,
    ):
        self.jobs = jobs
        self.notifier = notifier
        self.pipeline_runner = pipeline_runner

    async def execute(self, user_id: int, url: str):
        logger.info("Maybe url: %s", url)

        parsed_url = urlparse(url)
        if " " in url or not parsed_url.scheme or not parsed_url.netloc:
            await self.notifier.notify(user_id, MessageType.WRONG_URL, url=url)
            return

        logger.info("Creating new job for user %s", user_id)

        new_job = TranscriptionJob(
            user_id=user_id,
            file_id=url,
            original_filename=None,
        )

        # Сохраняем состояние для задачи
        await self.jobs.save(new_job)

        self.pipeline_runner.run_pipeline(new_job.id)

        await self.notifier.notify(user_id, MessageType.FILE_IS_DOWNLOADING)
