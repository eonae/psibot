from aiogram import Router  # type: ignore
from aiogram.filters import Command  # type: ignore

from .handle_audio_file import handle_audio_file
from .handle_confirmation import handle_confirmation
from .handle_rejection import handle_rejection
from .handle_start import handle_start

router = Router()

router.message.register(handle_audio_file)
router.callback_query.register(handle_confirmation, lambda c: c.data == "confirm")
router.callback_query.register(handle_rejection, lambda c: c.data == "reject")
router.message.register(handle_start, Command("start"))
