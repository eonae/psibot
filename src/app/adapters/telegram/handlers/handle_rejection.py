from aiogram.types import CallbackQuery  # type: ignore

from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleRejectionUseCase


async def handle_rejection(callback: CallbackQuery) -> None:
    """Обработчик отклонения результата"""
    use_case = HandleRejectionUseCase(
        jobs=make_jobs_repository(),
        notifier=TelegramNotifier(bot),
    )

    await use_case.execute(callback.from_user.id)
