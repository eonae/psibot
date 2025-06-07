"""
Входная точка для запуска бота и API сервера.
"""

import asyncio
import threading
from aiogram import Dispatcher  # type: ignore
import uvicorn  # type: ignore
from src.app.api.main import app
from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram.handlers import router


def run_api_server():
    """
    Запускает FastAPI сервер в отдельном потоке.
    """
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


async def main():
    """
    Запускает бота и API сервер.
    """
    # Регистрируем обработчики
    dp = Dispatcher()
    dp.include_router(router)

    # Запускаем API сервер в отдельном потоке
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# Для poetry
def run_main_async():
    """Entry point for poetry script"""
    asyncio.run(main())
