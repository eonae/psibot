from aiogram.types import Message  # type: ignore

from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram.telegram_notifier import TelegramNotifier
from src.app.core.ports import MessageType


async def handle_start(message: Message) -> None:
    notifier = TelegramNotifier(bot)
    await notifier.notify(message.chat.id, MessageType.WELCOME)
