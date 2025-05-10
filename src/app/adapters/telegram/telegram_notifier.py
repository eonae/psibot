from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.app.core.ports import Message, MessageType, Notifier
from .message_handler import TelegramMessageHandler


class TelegramNotifier(Notifier):
    def __init__(self, bot: Bot) -> None:
        self.handler = TelegramMessageHandler(bot)

    async def notify(self, user_id: int, message_type: MessageType, **params) -> None:
        message = Message(message_type, params)
        await self.handler.send_message(user_id, message)

    async def send_result_with_confirmation(
        self, user_id: int, file: bytes, filename: str, job_id: str
    ) -> None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Подтвердить", callback_data="confirm"
                    ),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data="reject"),
                ]
            ]
        )

        message = Message(
            MessageType.TRANSCRIPTION_COMPLETED,
            {"job_id": job_id},
        )

        await self.handler.send_document(
            user_id,
            file,
            filename,
            message,
            reply_markup=keyboard,
        )
