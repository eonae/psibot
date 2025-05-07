from aiogram import Bot  # type: ignore
from aiogram.types import (  # type: ignore
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.app.core.ports import Notifier

from .templates import (
    CONVERT_COMPLETED,
    CONVERT_FAILED,
    DIARIZATION_COMPLETED,
    DIARIZATION_FAILED,
    DOWNLOAD_COMPLETED,
    DOWNLOAD_FAILED,
    MERGE_COMPLETED,
    MERGE_FAILED,
    POSTPROCESSING_COMPLETED,
    POSTPROCESSING_FAILED,
    TRANSCRIBING_COMPLETED,
    TRANSCRIBING_FAILED,
    TRANSCRIPTION_COMPLETED,
    TRANSCRIPTION_FAILED,
    TRANSCRIPTION_STARTED,
    WELCOME_MESSAGE,
)


class TelegramNotifier(Notifier):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def notify_welcome(self, user_id: int) -> None:
        """Отправляет приветственное сообщение"""
        await self.bot.send_message(user_id, WELCOME_MESSAGE)

    async def notify_download_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, DOWNLOAD_COMPLETED)

    async def notify_download_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, DOWNLOAD_FAILED)

    async def notify_conversion_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, CONVERT_COMPLETED)

    async def notify_conversion_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, CONVERT_FAILED)

    async def notify_diarization_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, DIARIZATION_COMPLETED)

    async def notify_diarization_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, DIARIZATION_FAILED)

    async def notify_transcribing_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, TRANSCRIBING_COMPLETED)

    async def notify_transcribing_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, TRANSCRIBING_FAILED)

    async def notify_merge_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, MERGE_COMPLETED)

    async def notify_merge_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, MERGE_FAILED)

    async def notify_postprocessing_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, POSTPROCESSING_COMPLETED)

    async def notify_postprocessing_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, POSTPROCESSING_FAILED)

    async def notify_transcription_started(self, user_id: int) -> None:
        await self.bot.send_message(user_id, TRANSCRIPTION_STARTED)

    async def notify_transcription_failed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, TRANSCRIPTION_FAILED)

    async def notify_transcription_completed(self, user_id: int) -> None:
        await self.bot.send_message(user_id, TRANSCRIPTION_COMPLETED)

    async def send_result_with_confirmation(
        self, user_id: int, file: bytes, filename: str
    ) -> None:
        caption = (
            "✅ Обработка завершена! Проверьте результат и подтвердите сохранение:"
        )
        # Отправляем клавиатуру с подтверждением
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

        # Отправляем файл с результатом
        await self.bot.send_document(
            user_id,
            document=BufferedInputFile(file, filename=filename),
            caption=caption,
            reply_markup=keyboard,
        )
