import logging
from pathlib import Path

from src.app.adapters.files import storage
from src.app.core.services import ConversionService

logger = logging.getLogger(__name__)


def convert_to_wav_task(source_filename: str, target_filename: str) -> None:
    """Конвертирует аудиофайл в WAV, если он изначально в другом формате

    Args:
        source_filename: Путь к исходному аудиофайлу
        target_filename: Путь для сохранения WAV файла
    """

    conversion_service = ConversionService(storage)
    conversion_service.convert_to_wav(Path(source_filename), Path(target_filename))
