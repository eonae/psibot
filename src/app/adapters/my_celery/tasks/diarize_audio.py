from pathlib import Path

from src.app.adapters.files import storage
from src.app.adapters.ml import PyannoteDiarizer
from src.app.config import Config
from src.app.core.services import DiarizationService


def diarize_audio_task(wav_filename: str, target_filename: str) -> None:
    """Определяет спикеров на аудиозаписи и сохраняет результат в хранилище

    Args:
        wav_filename: Путь к WAV файлу
        target_filename: Путь для сохранения результата
    """

    diarizer = PyannoteDiarizer.from_config(Config())

    diarizer_service = DiarizationService(storage, diarizer)
    diarizer_service.diarize(Path(wav_filename), Path(target_filename))
