from aiogram import Bot  # type: ignore
from aiogram.types import CallbackQuery, Message  # type: ignore

from src.app.core.ports import Responder

from .templates import (
    FILE_IS_DOWNLOADING,
    FILE_MISSING,
    FILE_SIZE_MISSING,
    FILE_SIZE_TOO_LARGE,
    NO_JOBS_MESSAGE,
    WRONG_MIME_TYPE,
)


class TelegramResponder(Responder):
    def __init__(self, callback_or_message: CallbackQuery | Message, bot: Bot) -> None:
        self.callback_or_message = callback_or_message
        self.bot = bot

    async def reply_wrong_mime_type(self, mime_type: str) -> None:
        await self._reply(WRONG_MIME_TYPE.format(mime_type=mime_type))

    async def reply_file_size_missing(self) -> None:
        await self._reply(FILE_SIZE_MISSING)

    async def notify_file_missing(self) -> None:
        await self._reply(FILE_MISSING)

    async def reply_file_size_too_large(self, max_size: int, size: int) -> None:
        mb = round(size / 1024 / 1024, 1)
        await self._reply(FILE_SIZE_TOO_LARGE.format(max_size=max_size, size=mb))

    async def reply_file_is_downloading(self) -> None:
        await self._reply(FILE_IS_DOWNLOADING)

    async def reply_confirmed(self) -> None:
        """Отправляет уведомление о подтверждении результата"""
        await self._reply("✅ Результат подтвержден")

    async def reply_rejected(self) -> None:
        """Отправляет уведомление об отклонении результата"""
        await self._reply("❌ Результат отклонен")

    async def reply_job_wrong_status(self) -> None:
        """Отправляет уведомление о неправильном статусе задачи"""
        await self._reply("Задача не находится в статусе ожидания подтверждения")

    async def reply_no_jobs(self) -> None:
        """Отправляет уведомление об отсутствии активных задач"""
        await self._reply(NO_JOBS_MESSAGE)

    async def _reply(self, msg: str, **kwargs) -> None:
        if isinstance(self.callback_or_message, CallbackQuery):
            message = self.callback_or_message.message

            if not isinstance(message, Message):
                # Можно также отправить уведомление (toast), если нужно
                await self.callback_or_message.answer(
                    text=msg, **kwargs
                )  # Просто скрыть "часики"
                return

            if message.text is not None:
                await message.edit_text(msg)
            elif message.caption is not None:
                await message.edit_caption(msg)
            elif message.reply_markup is not None:
                await message.edit_reply_markup(reply_markup=None)

            # print("answer")
            # await message.answer(text=msg, **kwargs)

            return

        # Ответ на сообщение
        await self.callback_or_message.answer(
            msg, reply_to_message_id=self.callback_or_message.message_id, **kwargs
        )
