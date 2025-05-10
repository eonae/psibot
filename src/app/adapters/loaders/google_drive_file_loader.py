import logging
import re
from urllib.parse import urlparse

from src.app.adapters.loaders.base_loader import BaseLoader

logger = logging.getLogger(__name__)


class GoogleDriveFileLoader(BaseLoader):
    def is_valid_file_id(self, file_id: str) -> bool:
        parsed_url = urlparse(file_id)

        if "drive.google.com" not in parsed_url.netloc:
            return False

        if not re.search(r"/file/d/([^/]+)", parsed_url.path):
            return False

        return True

    def _get_download_url(self, file_id: str) -> str:
        """Получает прямую ссылку для скачивания с Google Drive.

        Args:
            file_id: идентификатор или публичная ссылка на файл

        Returns:
            str: Прямая ссылка для скачивания
        """
        match = re.search(r"/file/d/([^/]+)", file_id)
        if not match:
            raise ValueError("Could not extract file ID from URL")

        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
