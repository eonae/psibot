"""
Роутер для обработки сообщений от Telegram.
"""

from aiogram import Router  # type: ignore
from aiogram.filters import Command  # type: ignore
from aiogram import F

from src.app.adapters.telegram.handlers.handle_audio_url import handle_audio_url  # type: ignore

from .handle_audio_file import handle_audio_file
from .handle_confirmation import handle_confirmation
from .handle_rejection import handle_rejection
from .handle_start import handle_start
from .handle_webapp import handle_webapp

router = Router()

router.message.register(handle_start, Command("start"))
router.message.register(handle_webapp, Command("webapp"))
router.message.register(handle_audio_file, F.voice)
router.message.register(handle_audio_file, F.document)
router.message.register(handle_audio_file, F.audio)
router.message.register(handle_audio_url)
router.callback_query.register(handle_confirmation, lambda c: c.data == "confirm")
router.callback_query.register(handle_rejection, lambda c: c.data == "reject")
