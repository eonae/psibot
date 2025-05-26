"""
Обработчик команды /audio_url.
"""

from aiogram.types import Message  # type: ignore

from src.app.adapters.celery_runner import CeleryRunner
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleNewUrlUseCase
from src.app.core.ports import MessageType


async def handle_audio_url(message: Message) -> None:
    """Обработчик команды /audio_url"""

    notifier = TelegramNotifier(bot)

    url = message.text
    if not url:
        await notifier.notify(message.chat.id, MessageType.WRONG_URL)
        return

    use_case = HandleNewUrlUseCase(
        jobs=make_jobs_repository(),
        pipeline_runner=CeleryRunner(),
        notifier=notifier,
    )

    await use_case.execute(
        message.chat.id,
        url=url,
    )
