"""
Обработчик команды /webapp.
"""

from aiogram.types import Message  # type: ignore

from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram.telegram_notifier import TelegramNotifier
from src.app.config import Config

config = Config()


async def handle_webapp(message: Message) -> None:
    """Обработчик команды /webapp"""
    notifier = TelegramNotifier(bot)

    await notifier.send_greetings(message.chat.id)
