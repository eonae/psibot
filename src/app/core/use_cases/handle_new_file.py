import logging
from datetime import datetime

from src.app.core.models import InputFileDTO, TranscriptionJob
from src.app.core.models.transcription_job_status import JobStatus
from src.app.core.ports import JobsRepository, Responder, TasksScheduler

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024


class HandleNewFileUseCase:
    def __init__(
        self,
        jobs: JobsRepository,
        responder: Responder,
        tasks_scheduler: TasksScheduler,
    ):
        self.jobs = jobs
        self.responder = responder
        self.tasks_scheduler = tasks_scheduler

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
            await self.responder.reply_wrong_mime_type(mime_type)
            return

        if size is None:
            await self.responder.reply_file_size_missing()
            return

        if size > MAX_FILE_SIZE:
            await self.responder.reply_file_size_too_large(MAX_FILE_SIZE, size)
            return

        logger.info("Creating new job for user %s", user_id)

        new_job = TranscriptionJob(
            user_id=user_id,
            file_id=file_id,
            original_filename=original_filename,
        )

        new_job.to_stage(JobStatus.DOWNLOADING)

        self.tasks_scheduler.schedule(
            task_name="download",
            job_id=new_job.id,
            file_id=file_id,
            target_filename=str(new_job.files.wav),
        )

        # Сохраняем состояние для задачи
        await self.jobs.save(new_job)

        await self.responder.reply_file_is_downloading()
