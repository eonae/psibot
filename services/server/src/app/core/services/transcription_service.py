import logging
import tempfile
from pathlib import Path

from src.app.adapters.files.singleton import storage
from src.app.core.ports import FileStorage
from src.app.core.ports.ml import SpeechToText

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self, storage: FileStorage, stt: SpeechToText):
        self.storage = storage
        self.stt = stt

    def transcribe(self, wav_filename: Path, target_filename: Path) -> None:
        """Транскрибация аудио файла

        Args:
        wav_filename: Путь к WAV файлу
        target_filename: Путь для сохранения результата
        """
        logger.info("🎯 Starting transcription of %s...", wav_filename)

        # Читаем файл из хранилища
        audio_data = storage.read(Path(wav_filename))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()  # обязательно, чтобы всё записалось на диск

            transcription = self.stt.transcribe(Path(tmp.name))

            # Сохраняем результат
            storage.save(str(transcription).encode(), Path(target_filename))

            logger.info("✅ Transcription completed: %s", target_filename)
