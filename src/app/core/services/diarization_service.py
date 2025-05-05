from pathlib import Path
import tempfile
import logging

from src.app.core.ports import FileStorage
from src.app.core.ports.ml import Diarizer
from src.shared.logging import log_time

logger = logging.getLogger(__name__)


class DiarizationService:
    def __init__(self, storage: FileStorage, diarizer: Diarizer):
        self.storage = storage
        self.diarizer = diarizer

    @log_time
    def diarize(self, wav_filename: Path, target_filename: Path) -> None:
        logger.info("🎯 Starting diarization of %s...", target_filename)

        audio_data = self.storage.read(wav_filename)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()  # обязательно, чтобы всё записалось на диск

            tmp_path = Path(tmp.name)

            diarization = self.diarizer.diarize(tmp_path)
            diarization_bytes = str(diarization).encode()
            self.storage.save(diarization_bytes, target_filename)

            logger.info("✅ Diarization completed: %s", target_filename)
