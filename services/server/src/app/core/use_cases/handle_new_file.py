"""
Обработчик нового файла.
"""

import logging
from datetime import datetime
from pathlib import Path

from src.app.core.models import TranscriptionJob
from src.app.core.models.input_file_dto import (
    DownloadableFileDTO,
    DownloadedFileDTO,
    TelegramFileDTO,
)
from src.app.core.models.transcription_job import FileSource, SourceType
from src.app.core.ports import JobsRepository, MessageType, Notifier, PipelineRunner
from src.app.core.ports.file_storage import FileStorage

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024

InputFile = TelegramFileDTO | DownloadedFileDTO | DownloadableFileDTO


class HandleNewFileUseCase:
    """
    Обработчик нового файла.
    """

    def __init__(
        self,
        jobs: JobsRepository,
        notifier: Notifier,
        storage: FileStorage,
        pipeline_runner: PipelineRunner,
    ):
        self.jobs = jobs
        self.notifier = notifier
        self.storage = storage
        self.pipeline_runner = pipeline_runner

    async def execute(
        self, user_id: int, input_file: TelegramFileDTO | DownloadedFileDTO
    ):
        """
        Выполняет обработку нового файла.
        """

        mime_type = input_file.mime_type or "unknown"
        size = input_file.size
        original_filename = (
            input_file.filename
            or f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_voice.ogg"
        )

        logger.info("File name: %s", original_filename)
        logger.info("File size: %s", size)
        logger.info("File mime_type: %s", mime_type)

        file_source = self._get_file_source(input_file)

        should_download = isinstance(input_file, TelegramFileDTO)

        logger.info("File source: %s (%s)", file_source.value, file_source.type)
        logger.info("Should download: %s", should_download)

        if not mime_type.startswith("audio/"):
            await self.notifier.notify(
                user_id, MessageType.WRONG_MIME_TYPE, mime_type=mime_type
            )
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
            source=file_source,
            original_filename=original_filename,
        )

        self.pipeline_runner.run_pipeline(new_job.id, should_download=should_download)

        # Сохраняем состояние для задачи
        await self.jobs.save(new_job)

        await self.notifier.notify(user_id, MessageType.FILE_IS_DOWNLOADING)

    def _get_file_source(self, input_file: InputFile) -> FileSource:
        if isinstance(input_file, TelegramFileDTO):
            return FileSource(
                type=SourceType.TELEGRAM_FILE_ID,
                value=input_file.file_id,
            )

        if isinstance(input_file, DownloadableFileDTO):
            return FileSource(
                type=SourceType.UPLOAD_URL,
                value=input_file.url,
            )

        if not input_file.filename:
            raise ValueError("Filename is required for downloaded file")

        self.storage.save(input_file.content, filename=Path(input_file.filename))

        return FileSource(
            type=SourceType.DOWNLOADED_FILE_PATH,
            value=input_file.content.decode("utf-8"),
        )
