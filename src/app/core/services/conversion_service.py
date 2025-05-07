import logging
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

        # Загружаем аудио из байтов через BytesIO
        # y - numpy массив с аудио данными (амплитуда звука)
        # sr - частота дискретизации (количество сэмплов в секунду)
        y, sr = librosa.load(BytesIO(audio_data), sr=SAMPLE_RATE)

        # Сохраняем в WAV используя soundfile (sf) через BytesIO
        buffer = BytesIO()
        sf.write(buffer, y, sr)
        buffer.seek(0)

        # Записываем через storage
        self.storage.save(buffer.getvalue(), target_filename)
        logger.info("✅ Conversion completed: %s", target_filename)
