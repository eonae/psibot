from aiogram.types import Message  # type: ignore

from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram.telegram_notifier import TelegramNotifier


async def handle_start(message: Message) -> None:
    """Обработчик команды /start"""
    notifier = TelegramNotifier(bot)
    await notifier.notify_welcome(message.chat.id)
