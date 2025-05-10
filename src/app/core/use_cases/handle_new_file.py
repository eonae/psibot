import logging
from datetime import datetime

from src.app.core.models import InputFileDTO, TranscriptionJob
from src.app.core.ports import JobsRepository, Notifier, PipelineRunner, MessageType

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024


class HandleNewFileUseCase:
    def __init__(
        self,
        jobs: JobsRepository,
        notifier: Notifier,
        pipeline_runner: PipelineRunner,
    ):
        self.jobs = jobs
        self.notifier = notifier
        self.pipeline_runner = pipeline_runner

    async def execute(self, user_id: int, input_file: InputFileDTO):
        mime_type = input_file.mime_type or "unknown"
        file_id, size = input_file.file_id, input_file.size
        original_filename = (
            input_file.filename
            or f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_voice.ogg"
        )

        logger.info("File name: %s", original_filename)
        logger.info("File id: %s", file_id)
        logger.info("File size: %s", size)
        logger.info("File mime_type: %s", mime_type)

        if not mime_type.startswith("audio/"):
            await self.notifier.notify(user_id, MessageType.WRONG_MIME_TYPE, mime_type=mime_type)
            return

        if size is None:
            await self.notifier.notify(user_id, MessageType.FILE_SIZE_MISSING)
            return

        if size > MAX_FILE_SIZE:
            await self.notifier.notify(
                user_id,
                MessageType.FILE_SIZE_TOO_LARGE,
                max_size=MAX_FILE_SIZE,
                size=size,
            )
            return

        logger.info("Creating new job for user %s", user_id)

        new_job = TranscriptionJob(
            user_id=user_id,
            file_id=file_id,
            original_filename=original_filename,
        )

        self.pipeline_runner.run_pipeline(new_job.id)

        # Сохраняем состояние для задачи
        await self.jobs.save(new_job)

        await self.notifier.notify(user_id, MessageType.FILE_IS_DOWNLOADING)
