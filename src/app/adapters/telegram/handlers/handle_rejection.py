from aiogram.types import CallbackQuery  # type: ignore

from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.telegram import TelegramResponder
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleRejectionUseCase


async def handle_rejection(callback: CallbackQuery) -> None:
    """Обработчик отклонения результата"""
    # Создаем use case
    use_case = HandleRejectionUseCase(
        jobs=make_jobs_repository(),
        responder=TelegramResponder(callback, bot),
    )

    # Выполняем use case
    await use_case.execute(callback.from_user.id)
