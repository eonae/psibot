"""
Обработчик подтверждения результата.
"""

from aiogram.types import CallbackQuery  # type: ignore

from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleConfirmationUseCase


async def handle_confirmation(callback: CallbackQuery) -> None:
    """Обработчик подтверждения результата"""

    use_case = HandleConfirmationUseCase(
        jobs=make_jobs_repository(),
        file_storage=storage,
        notifier=TelegramNotifier(bot),
    )

    await use_case.execute(callback.from_user.id)
