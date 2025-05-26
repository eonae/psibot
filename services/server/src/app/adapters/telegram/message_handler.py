"""
Обработчик сообщений для Telegram.
"""

import asyncio
import logging
from typing import Optional

from aiogram import Bot  # type: ignore

# pylint: disable=line-too-long
# flake8: noqa: E501
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramRetryAfter  # type: ignore
from aiogram.types import BufferedInputFile, CallbackQuery  # type: ignore
from aiogram.types import Message as TelegramMessage  # type: ignore
from aiogram.types import InlineKeyboardMarkup  # type: ignore
from src.app.core.ports import Message, MessageType

from .templates import (
    CONFIRMED,
    CONVERT_COMPLETED,
    CONVERT_FAILED,
    DIARIZATION_COMPLETED,
    DIARIZATION_FAILED,
    DOWNLOAD_COMPLETED,
    DOWNLOAD_FAILED,
    FILE_IS_DOWNLOADING,
    FILE_MISSING,
    FILE_SIZE_MISSING,
    FILE_SIZE_TOO_LARGE,
    JOB_WRONG_STATUS,
    MERGE_COMPLETED,
    MERGE_FAILED,
    NO_JOBS_MESSAGE,
    POSTPROCESSING_COMPLETED,
    POSTPROCESSING_FAILED,
    REJECTED,
    TRANSCRIPTION_COMPLETED,
    TRANSCRIPTION_FAILED,
    WELCOME_MESSAGE,
    WRONG_MIME_TYPE,
    WRONG_URL,
)

logger = logging.getLogger(__name__)


class TelegramMessageHandler:
    """
    Обработчик сообщений для Telegram.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._templates = {
            MessageType.FILE_IS_DOWNLOADING: FILE_IS_DOWNLOADING,
            MessageType.FILE_MISSING: FILE_MISSING,
            MessageType.WRONG_MIME_TYPE: WRONG_MIME_TYPE,
            MessageType.FILE_SIZE_MISSING: FILE_SIZE_MISSING,
            MessageType.FILE_SIZE_TOO_LARGE: FILE_SIZE_TOO_LARGE,
            MessageType.DOWNLOAD_COMPLETED: DOWNLOAD_COMPLETED,
            MessageType.DOWNLOAD_FAILED: DOWNLOAD_FAILED,
            MessageType.CONVERT_COMPLETED: CONVERT_COMPLETED,
            MessageType.CONVERT_FAILED: CONVERT_FAILED,
            MessageType.DIARIZATION_COMPLETED: DIARIZATION_COMPLETED,
            MessageType.DIARIZATION_FAILED: DIARIZATION_FAILED,
            MessageType.MERGE_COMPLETED: MERGE_COMPLETED,
            MessageType.MERGE_FAILED: MERGE_FAILED,
            MessageType.POSTPROCESSING_COMPLETED: POSTPROCESSING_COMPLETED,
            MessageType.POSTPROCESSING_FAILED: POSTPROCESSING_FAILED,
            MessageType.TRANSCRIPTION_FAILED: TRANSCRIPTION_FAILED,
            MessageType.TRANSCRIPTION_COMPLETED: TRANSCRIPTION_COMPLETED,
            MessageType.NO_JOBS: NO_JOBS_MESSAGE,
            MessageType.WELCOME: WELCOME_MESSAGE,
            MessageType.CONFIRMED: CONFIRMED,
            MessageType.REJECTED: REJECTED,
            MessageType.JOB_WRONG_STATUS: JOB_WRONG_STATUS,
            MessageType.WRONG_URL: WRONG_URL,
        }

    def _get_template(self, message: Message) -> str:
        return self._templates[message.type]

    async def _send_with_retry(
        self,
        send_func,
        *args,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        **kwargs,
    ) -> Optional[TelegramMessage]:
        delay = initial_delay
        last_error: Optional[TelegramAPIError] = None

        for attempt in range(max_retries):
            try:
                return await send_func(*args, **kwargs)
            except TelegramRetryAfter as e:
                wait_time = e.retry_after
                logger.warning(
                    "Rate limit hit, waiting %d seconds before retry. Attempt: %d/%d",
                    wait_time,
                    attempt + 1,
                    max_retries,
                )
                await asyncio.sleep(wait_time)
                last_error = e
            except TelegramBadRequest as e:
                logger.error("Bad request error: %s", e)
                raise
            except TelegramAPIError as e:
                logger.error("Telegram API error: %s", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
                    last_error = e
                else:
                    raise

        if last_error:
            raise last_error

        return None

    async def send_message(
        self,
        user_id: int,
        message: Message,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> None:
        """
        Отправляет сообщение пользователю.
        """

        try:
            template = self._get_template(message)
            text = template.format(**message.params)
            await self._send_with_retry(
                self.bot.send_message,
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
            )
        except TelegramBadRequest as e:
            logger.error("Failed to send message to user %d: %s", user_id, e)
            raise
        except Exception as e:
            logger.error(
                "Unexpected error while sending message to user %d: %s", user_id, e
            )
            raise

    async def send_document(
        self,
        user_id: int,
        file: bytes,
        filename: str,
        message: Message,
        reply_markup=None,
    ) -> None:
        """
        Отправляет документ пользователю.
        """

        try:
            template = self._get_template(message)
            text = template.format(**message.params)
            await self._send_with_retry(
                self.bot.send_document,
                chat_id=user_id,
                document=BufferedInputFile(file, filename=filename),
                caption=text,
                reply_markup=reply_markup,
            )
        except TelegramBadRequest as e:
            logger.error("Failed to send document to user %d: %s", user_id, e)
            raise
        except Exception as e:
            logger.error(
                "Unexpected error while sending document to user %d: %s", user_id, e
            )
            raise

    async def edit_message(
        self,
        callback_or_message: CallbackQuery | TelegramMessage,
        message: Message,
    ) -> None:
        """
        Редактирует сообщение.
        """

        try:
            template = self._get_template(message)
            text = template.format(**message.params)

            if isinstance(callback_or_message, CallbackQuery):
                msg = callback_or_message.message
                if not isinstance(msg, TelegramMessage):
                    await callback_or_message.answer(text=text)
                    return

                if msg.text is not None:
                    await self._send_with_retry(msg.edit_text, text=text)
                elif msg.caption is not None:
                    await self._send_with_retry(msg.edit_caption, caption=text)
                elif msg.reply_markup is not None:
                    await self._send_with_retry(
                        msg.edit_reply_markup, reply_markup=None
                    )
                return

            await self._send_with_retry(
                callback_or_message.answer,
                text=text,
                reply_to_message_id=callback_or_message.message_id,
            )
        except TelegramBadRequest as e:
            logger.error("Failed to edit message: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error while editing message: %s", e)
            raise
