from aiogram import Bot  # type: ignore

from src.app.config import Config

config = Config()

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
