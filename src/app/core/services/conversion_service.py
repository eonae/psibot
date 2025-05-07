import logging
import tempfile
from io import BytesIO
from pathlib import Path

import librosa
import soundfile as sf  # type: ignore

from src.app.core.ports import FileStorage
from src.shared.logging import log_time

logger = logging.getLogger(__name__)

# Частота дискретизации для WAV файлов
SAMPLE_RATE = 16000


class ConversionService:
    def __init__(self, storage: FileStorage):
        self.storage = storage

    @log_time
    def convert_to_wav(self, source_filename: Path, target_filename: Path) -> None:
        """Конвертирует аудиофайл в WAV (если он уже WAV - просто копируем)

        Args:
            source_filename: Путь к исходному аудиофайлу
            target_filename: Путь для сохранения WAV файла
        """
        # Если исходный файл уже WAV - просто копируем
        if source_filename.suffix.lower() == ".wav":
            logger.info("📋 Source file is already WAV, copying to %s", target_filename)
            self.storage.copy(source_filename, target_filename)
            return

        logger.info("🔄 Converting %s to WAV...", source_filename)

        # Читаем исходный файл
        audio_data = self.storage.read(source_filename)

        with tempfile.NamedTemporaryFile(suffix=source_filename.suffix, delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()  # обязательно, чтобы всё записалось на диск

            print('TEMPORARY FILE:', tmp.name)

            # Загружаем аудио из временного файла
            y, sr = librosa.load(tmp.name, sr=SAMPLE_RATE)

            # Сохраняем в WAV используя soundfile (sf) через BytesIO
            buffer = BytesIO()
            sf.write(buffer, y, sr)
            buffer.seek(0)

            # Записываем через storage
            self.storage.save(buffer.getvalue(), target_filename)
            logger.info("✅ Conversion completed: %s", target_filename)
