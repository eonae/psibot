from aiogram.types import CallbackQuery  # type: ignore

from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.telegram import TelegramResponder
from src.app.adapters.telegram.singleton import bot
from src.app.core.use_cases import HandleConfirmationUseCase


async def handle_confirmation(callback: CallbackQuery) -> None:
    """Обработчик подтверждения результата"""
    # Создаем use case
    use_case = HandleConfirmationUseCase(
        jobs=make_jobs_repository(),
        file_storage=storage,
        responder=TelegramResponder(callback, bot),
    )

    # Выполняем use case
    await use_case.execute(callback.from_user.id)
