import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _must_load(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} is not set")
    return value


@dataclass
class Config:
    """Конфигурация приложения"""

    # Telegram
    TELEGRAM_BOT_TOKEN = _must_load("TELEGRAM_BOT_TOKEN")

    # Hugging Face
    HUGGING_FACE_TOKEN = _must_load("HUGGING_FACE_TOKEN")

    # Celery
    CELERY_BROKER_URL = _must_load("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = _must_load("CELERY_RESULT_BACKEND")

    # Yandex Cloud
    YC_FOLDER_ID = _must_load("YC_FOLDER_ID")
    YC_SERVICE_ACCOUNT_ID = _must_load("YC_SERVICE_ACCOUNT_ID")
    YC_SERVICE_ACCOUNT_PRIVATE_KEY_ID = _must_load("YC_SERVICE_ACCOUNT_PRIVATE_KEY_ID")
    YC_SERVICE_ACCOUNT_PRIVATE_KEY = _must_load("YC_SERVICE_ACCOUNT_PRIVATE_KEY")
    YC_API_KEY = _must_load("YC_API_KEY")

    # Yandex Cloud S3
    YC_S3_ENDPOINT = _must_load("YC_S3_ENDPOINT")
    YC_ACCESS_KEY_ID = _must_load("YC_ACCESS_KEY_ID")
    YC_SECRET_ACCESS_KEY = _must_load("YC_SECRET_ACCESS_KEY")
    YC_SPEECH_KIT_BUCKET_NAME = os.getenv("YC_SPEECH_KIT_BUCKET_NAME", "speech-kit-wav")

    # OpenRouter ML
    OPENROUTER_API_KEY = _must_load("OPENROUTER_API_KEY")

    # Директории
    AUDIO_DIR = Path(os.getenv("AUDIO_DIR", "audio"))
