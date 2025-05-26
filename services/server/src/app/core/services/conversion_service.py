"""
Сервис для конвертации аудио-файлов.
"""

import logging
import subprocess
import tempfile
from pathlib import Path

from src.app.core.ports import FileStorage
from src.shared.logging import log_time

logger = logging.getLogger(__name__)


class ConversionService:
    """Сервис для конвертации аудио-файлов."""

    def __init__(self, storage: FileStorage):
        self.storage = storage

    @log_time
    def convert_to_wav(
        self,
        source_filename: Path,
        target_filename: Path,
    ) -> None:
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

        ext = source_filename.suffix
        wav = ".wav"

        with (
            tempfile.NamedTemporaryFile(suffix=ext, delete=True) as input_tmp,
            tempfile.NamedTemporaryFile(suffix=wav, delete=True) as output_tmp,
        ):

            # Записываем входной файл
            input_tmp.write(audio_data)
            input_tmp.flush()

            # Запускаем ffmpeg для конвертации
            cmd = [
                "ffmpeg",
                "-y",  # Перезаписывать выходной файл если существует
                "-i",
                input_tmp.name,  # Входной файл
                "-acodec",
                "pcm_s16le",  # Кодек для WAV
                "-ar",
                "16000",  # Частота дискретизации
                "-ac",
                "1",  # Моно
                output_tmp.name,  # Выходной файл
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logger.error("FFmpeg error: %s", e.stderr)

                raise RuntimeError(f"Failed to convert audio: {e.stderr}") from e

            # Читаем результат и сохраняем
            with open(output_tmp.name, "rb") as f:
                wav_data = f.read()

            self.storage.save(wav_data, target_filename)
            logger.info("✅ Conversion completed: %s", target_filename)
