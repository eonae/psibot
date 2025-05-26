"""
Входная точка для запуска бота.
"""

import asyncio
import logging

from aiogram import Dispatcher  # type: ignore

from src.app.adapters.telegram.handlers import router
from src.app.adapters.telegram.singleton import bot
from src.shared.logging import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Запуск бота.
    """

    # Настраиваем логирование
    setup_logging(level=logging.DEBUG)

    # Проверяем токен бота
    logger.info("Checking bot token...")
    if not bot.token:
        logger.error("Bot token is not set!")
        return

    # Создаем диспетчер
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# Для poetry
def run_main_async():
    """Entry point for poetry script"""
    asyncio.run(main())
