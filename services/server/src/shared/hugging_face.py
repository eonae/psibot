"""Модуль для работы с Hugging Face pipeline"""

import logging

from pyannote.audio import Pipeline  # type: ignore

from src.shared.device import get_device

logger = logging.getLogger(__name__)


def create_pipeline(model_name: str, token: str) -> Pipeline:
    """Создает и возвращает pipeline для диаризации"""
    logger.info("🔽 Downloading pipeline from Hugging Face...")
    pipeline = Pipeline.from_pretrained(model_name, use_auth_token=token)

    # Перемещаем pipeline на оптимальное устройство
    device = get_device()
    pipeline = pipeline.to(device)
    logger.info("✅ Pipeline is downloaded and moved to %s", device)

    return pipeline
