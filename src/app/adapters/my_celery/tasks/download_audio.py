from pathlib import Path

from src.app.adapters.files import storage
from src.app.adapters.telegram import TelegramFileLoader
from src.app.core.services import DownloadingService


def download_audio_task(file_id: str, target_filename: str) -> None:
    """Скачивает аудиофайл из Telegram и сохраняет в хранилище

    Args:
        file_id: ID файла в Telegram
        target_filename: Имя файла для сохранения
    """

    loader = TelegramFileLoader()
    downloading_service = DownloadingService(storage, loader)
    downloading_service.download_audio(file_id, Path(target_filename))
