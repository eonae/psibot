import logging
import re

import requests  # type: ignore

from src.app.config import Config
from src.app.adapters.loaders.base_loader import BaseLoader

config = Config()

BOT = f"bot{config.TELEGRAM_BOT_TOKEN}"
TELEGRAM_BASE_URL = "https://api.telegram.org"

logger = logging.getLogger(__name__)


class TelegramFileLoader(BaseLoader):
    def is_valid_file_id(self, file_id: str) -> bool:
        """Проверяет валидность ID файла в Telegram.

        Args:
            file_id: ID файла в Telegram

        Returns:
            bool: True, если ID валиден, False - иначе
        """
        # В Telegram file_id - это строка, которая может содержать только
        # буквы, цифры, подчеркивания и дефисы
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", file_id))

    def _get_download_url(self, file_id: str) -> str:
        """Получает прямую ссылку для скачивания файла из Telegram.

        Args:
            file_id: ID файла в Telegram

        Returns:
            str: Прямая ссылка для скачивания

        Raises:
            RuntimeError: Если не удалось получить путь к файлу
        """
        # Получаем информацию о файле
        url = f"{TELEGRAM_BASE_URL}/{BOT}/getFile"
        response = requests.get(url, params={"file_id": file_id}, timeout=10)
        response.raise_for_status()

        try:
            path = response.json()["result"]["file_path"]
        except (KeyError, TypeError) as e:
            raise RuntimeError(f"Failed to get file path: {e}") from e

        return f"{TELEGRAM_BASE_URL}/file/{BOT}/{path}"
