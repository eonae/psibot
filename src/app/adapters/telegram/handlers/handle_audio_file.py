from aiogram.types import Message, Voice  # type: ignore

from src.app.adapters.my_celery.singleton import my_celery_app
from src.app.adapters.db import jobs_repository
from src.app.adapters.telegram import TelegramResponder
from src.app.adapters.telegram.singleton import bot
from src.app.core.models import InputFileDTO
from src.app.core.use_cases import HandleNewFileUseCase


async def handle_audio_file(message: Message) -> None:
    """Обработчик аудиофайла"""

    file = message.audio or message.document or message.voice
    if not file:
        return

    # Создаем use case
    use_case = HandleNewFileUseCase(
        jobs=jobs_repository,
        tasks_scheduler=my_celery_app,
        responder=TelegramResponder(message, bot),
    )

    # Выполняем use case
    await use_case.execute(
        message.chat.id,
        InputFileDTO(
            file_id=file.file_id,
            mime_type=file.mime_type,
            size=file.file_size,
            filename=(file.file_name if not isinstance(file, Voice) else None),
        ),
    )
