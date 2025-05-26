"""
Обработчик команды /help.
"""

from aiogram.types import Message  # type: ignore

from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram import TelegramNotifier
from src.app.core.ports import MessageType


async def handle_help(message: Message) -> None:
    """Обработчик команды /help"""

    notifier = TelegramNotifier(bot)
    await notifier.notify(message.chat.id, MessageType.HELP)
