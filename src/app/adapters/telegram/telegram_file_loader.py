import logging

import requests  # type: ignore

from src.app.config import Config
from src.app.core.ports import FileLoader
from src.shared.logging import log_time

config = Config()

BOT = f"bot{config.TELEGRAM_BOT_TOKEN}"
TELEGRAM_BASE_URL = "https://api.telegram.org"

logger = logging.getLogger(__name__)


class TelegramFileLoader(FileLoader):
    @log_time
    def load(self, file_id: str) -> bytes:
        """Скачивает аудиофайл из Telegram

        Args:
            file_id: ID файла в Telegram
        """

        # Получаем информацию о файле
        url = f"{TELEGRAM_BASE_URL}/{BOT}/getFile"
        response = requests.get(url, params={"file_id": file_id}, timeout=10)
        response.raise_for_status()
        path = response.json()["result"]["file_path"]

        # Скачиваем файл
        url = f"{TELEGRAM_BASE_URL}/file/{BOT}/{path}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.content
