import logging
from pathlib import Path

from src.app.core.ports import FileStorage, FileLoader
from src.shared.logging import log_time

logger = logging.getLogger(__name__)


class DownloadingService:
    def __init__(self, storage: FileStorage, loader: FileLoader):
        self.storage = storage
        self.loader = loader

    @log_time
    def download_audio(self, file_id: str, target_filename: Path) -> None:
        """Скачивает аудиофайл из Telegram

        Args:
            file_id: ID файла в Telegram
            target_filename: Имя файла для сохранения
        """

        content = self.loader.load(file_id)
        self.storage.save(content, target_filename)
        logger.info("✅ Audio file downloaded and saved: %s", target_filename)
