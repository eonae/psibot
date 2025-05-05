from typing import Any
from uuid import UUID

from lib.celery_reactive import Headers
from src.app.adapters.my_celery.singleton import my_celery_app
from src.app.adapters.db import jobs_repository
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleTranscriptionResultUseCase


async def handle_transcription_result(
    ex: Exception | None, _: Any | None, headers: Headers
):
    """Обработчик успешного завершения транскрибации аудио"""
    job_id = headers.get("job_id")
    assert job_id is not None

    use_case = HandleTranscriptionResultUseCase(
        jobs_repository=jobs_repository,
        tasks_scheduler=my_celery_app,
        notifier=TelegramNotifier(bot),
    )

    await use_case.execute(UUID(job_id), ex)
