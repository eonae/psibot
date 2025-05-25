import logging
import re
from urllib.parse import urlparse

import requests

from src.app.adapters.loaders.base_loader import BaseLoader

logger = logging.getLogger(__name__)


class YandexDiskFileLoader(BaseLoader):
    def is_valid_file_id(self, file_id: str) -> bool:
        """Проверяет валидность URL Яндекс.Диска.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            bool: True, если идентификатор валиден, False - иначе

        Raises:
            ValueError: Если URL не является ссылкой на Яндекс.Диск
        """
        parsed_url = urlparse(file_id)

        if "disk.yandex.ru" not in parsed_url.netloc:
            return False

        if not re.search(r"/d/([^/]+)", parsed_url.path):
            return False

        return True

    def _get_download_url(self, file_id: str) -> str:
        """Получает прямую ссылку для скачивания с Яндекс.Диска.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            str: Прямая ссылка для скачивания

        Raises:
            RuntimeError: Если не удалось получить прямую ссылку
        """

        # Получаем прямую ссылку на скачивание
        api_url = (
            f"https://cloud-api.yandex.net/v1/disk/public/resources"
            f"?public_key={file_id}"
        )

        try:
            # Получаем метаинформацию о файле
            response = requests.get(api_url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if "file" not in data:
                raise RuntimeError("No download link in response")

            return data["file"]

        except Exception as e:
            raise RuntimeError(f"Failed to get download URL: {e}") from e
