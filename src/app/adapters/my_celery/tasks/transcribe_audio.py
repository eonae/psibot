from pathlib import Path

from src.app.adapters.files import storage
from src.app.adapters.ml import YandexSpeechKit
from src.app.adapters.s3bucket import S3Bucket
from src.app.config import Config
from src.app.core.services import TranscriptionService


def transcribe_audio_task(wav_filename: str, target_filename: str) -> None:
    config = Config()
    bucket = S3Bucket(config)
    stt = YandexSpeechKit(
        api_key=config.YC_API_KEY,
        bucket=bucket,
    )

    transcription_service = TranscriptionService(storage, stt)
    transcription_service.transcribe(Path(wav_filename), Path(target_filename))
