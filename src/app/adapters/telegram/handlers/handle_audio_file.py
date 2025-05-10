from aiogram.types import Message, Voice  # type: ignore

from src.app.adapters.celery_runner import CeleryRunner
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.models import InputFileDTO
from src.app.core.ports import MessageType
from src.app.core.use_cases import HandleNewFileUseCase


async def handle_audio_file(message: Message) -> None:
    notifier = TelegramNotifier(bot)

    file = message.audio or message.document or message.voice
    if not file:
        await notifier.notify(message.chat.id, MessageType.FILE_MISSING)
        return

    use_case = HandleNewFileUseCase(
        jobs=make_jobs_repository(),
        pipeline_runner=CeleryRunner(),
        notifier=notifier,
    )

    await use_case.execute(
        message.chat.id,
        InputFileDTO(
            file_id=file.file_id,
            mime_type=file.mime_type,
            size=file.file_size,
            filename=(file.file_name if not isinstance(file, Voice) else None),
        ),
    )
