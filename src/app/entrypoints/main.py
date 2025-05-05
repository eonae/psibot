import asyncio
import logging

from aiogram import Dispatcher

from src.app.adapters.my_celery.result_handlers import (
    handle_convert_result,
    handle_diarization_result,
    handle_download_result,
    handle_merge_result,
    handle_postprocessing_result,
    handle_transcription_result,
)
from src.app.adapters.my_celery.singleton import my_celery_app
from src.app.adapters.telegram.handlers import router
from src.app.adapters.telegram.singleton import bot
from src.shared.logging import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
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

    my_celery_app.subscribe("download", handle_download_result)
    my_celery_app.subscribe("convert", handle_convert_result)
    my_celery_app.subscribe("diarize", handle_diarization_result)
    my_celery_app.subscribe("transcribe", handle_transcription_result)
    my_celery_app.subscribe("merge", handle_merge_result)
    my_celery_app.subscribe("postprocess", handle_postprocessing_result)

    try:
        # Запускаем бота
        logger.info("Starting celery results listener...")
        await my_celery_app.listen_results()
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        # Останавливаем celery_results при завершении
        await my_celery_app.stop_listening_results()


if __name__ == "__main__":
    asyncio.run(main())


# Для poetry
def run_main_async():
    """Entry point for poetry script"""
    asyncio.run(main())
