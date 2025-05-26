"""
Базовый класс для всех загрузчиков файлов.
"""

import logging
from abc import abstractmethod
from email.parser import HeaderParser
from typing import Tuple

import requests  # type: ignore

from src.app.core.ports import FileLoader
from src.shared.logging import log_time

logger = logging.getLogger(__name__)


class BaseLoader(FileLoader):
    """Базовый класс для всех загрузчиков файлов.

    Предоставляет общий функционал для скачивания файлов:
    - Проверка URL
    - Обработка ошибок
    """

    @abstractmethod
    def _get_download_url(self, file_id: str) -> str:
        """Получает прямую ссылку для скачивания.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            str: Прямая ссылка для скачивания

        Raises:
            ValueError: Если URL не поддерживается
        """

    @abstractmethod
    def is_valid_file_id(self, file_id: str) -> bool:
        """Проверяет валидность идентификатора файла.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            bool: True, если идентификатор валиден, False - иначе
        """

    def _extract_filename(self, header: str) -> str | None:
        """Извлекает имя файла из заголовка Content-Disposition.

        Args:
            header: значение заголовка Content-Disposition

        Returns:
            str | None: имя файла

        Raises:
            ValueError: если не удалось извлечь имя файла
        """
        parser = HeaderParser()
        msg = parser.parsestr(f"Content-Disposition: {header}")
        filename = msg.get_param("filename", header="content-disposition")

        if not filename:
            return None

        # Если имя файла пришло как tuple (RFC 2231)
        if isinstance(filename, tuple):
            charset, _, value = filename
            return value.encode("latin-1").decode(charset or "utf-8")

        # Если имя файла пришло как строка
        return filename.encode("latin-1").decode("utf-8")

    @log_time
    def load(self, file_id: str) -> Tuple[bytes, str | None]:
        """Загружает файл.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            Tuple[bytes, str]: Кортеж из содержимого файла и его имени

        Raises:
            RuntimeError: Если не удалось скачать файл
            ValueError: Если URL не валиден
        """
        if not self.is_valid_file_id(file_id):
            raise ValueError("Invalid file ID")

        logger.info("Getting download URL...")
        download_url = self._get_download_url(file_id)

        logger.info("Download URL: %s", download_url)

        try:
            # Скачиваем файл
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            # Получаем имя файла из Content-Disposition
            content_disposition = response.headers.get("Content-Disposition")
            if not content_disposition:
                raise ValueError("No Content-Disposition header")

            logger.debug("Content-Disposition: %s", content_disposition)

            # Извлекаем имя файла
            file_name = self._extract_filename(content_disposition)

            logger.debug("Extracted filename: %s", file_name)
            # Получаем размер файла
            total_size = int(response.headers.get("content-length", 0))

            # Скачиваем файл
            if total_size == 0:
                return response.content, file_name

            downloaded = 0
            chunks = []
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)

            logger.info("✅ File downloaded successfully (%d bytes)", downloaded)
            return b"".join(chunks), file_name

        except Exception as e:
            logger.error("❌ Error downloading file: %s", e)
            raise RuntimeError(f"Failed to download file: {e}") from e
