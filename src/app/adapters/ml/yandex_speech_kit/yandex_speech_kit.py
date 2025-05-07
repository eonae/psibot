import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Any

import requests

from src.app.core.models import (
    SegmentCollection,
    TranscriptionResult,
    TranscriptionSegment,
)
from src.app.core.ports import Bucket
from src.app.core.ports.ml import SpeechToText
from src.shared.logging import log_time

logger = logging.getLogger(__name__)

POLLING_INTERVAL = 5
STT_BASE_URL = "https://stt.api.cloud.yandex.net/stt/v3"
OPERATIONS_BASE_URL = "https://operation.api.cloud.yandex.net/operations"


class YandexSpeechKit(SpeechToText):
    def __init__(self, api_key: str, bucket: Bucket):
        self.bucket = bucket
        self.headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json",
        }

    @log_time
    def transcribe(self, audio_file: Path) -> SegmentCollection[TranscriptionSegment]:
        """Распознавание текста из аудио файла"""

        key = f"{audio_file}_{datetime.now()}"
        logger.info("🔼 Uploading file to storage: %s (key: %s)", audio_file, key)

        self.bucket.upload(audio_file, key)

        url = self.bucket.get_presigned_url(key)

        logger.info("🔗 File is uploaded to storage. Presigned URL: %s", url)

        logger.info("🌎 Sending async recognition request to Yandex SpeechKit")
        operation_id = self._recognize_file_async(url)
        logger.info("⏳ Operation created: %s", operation_id)

        while True:
            done = self._get_operation_status(operation_id)
            if done:
                logger.info("✅ Operation completed: %s", operation_id)
                break

            logger.info("⏳ Waiting for operation result: %s", operation_id)
            sleep(POLLING_INTERVAL)  # Ждем 5 секунд перед следующей проверкой

        logger.info("📦 Fetching recognition result: %s", operation_id)
        raw = self._get_recognition(operation_id)

        print(json.dumps(raw, indent=4))

        return self._parse_results(raw)

    # https://yandex.cloud/ru/docs/speechkit/stt-v3/api-ref/AsyncRecognizer/recognizeFile
    # Честно говоря, я не уверен, что параметры работают
    def _recognize_file_async(self, s3_url: str) -> str:
        url = f"{STT_BASE_URL}/recognizeFileAsync"
        data = {
            "uri": s3_url,
            "recognition_model": {
                "model": "general",
                "audio_processing_type": "FULL_DATA",
                "audio_format": {
                    "container_audio": {
                        "container_audio_type": "WAV",
                    },
                },
                "language_restriction": {
                    "restriction_type": "WHITELIST",
                    "language_codes": ["en-EN"],
                },
            },
            # Эти настройки не добавляют никаких новых данных в результат,
            # но если без них channelTag - всегда 0, то с ними speechkit
            # пытается разделять. Проблема в том, что в результате дорожки
            # накладываются друг на друга, и получается очень сложно обработать данные.
            #
            # "speaker_labeling": {
            #     "speaker_labeling": "SPEAKER_LABELING_ENABLED",
            # },
        }

        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response.raise_for_status()
        operation_id = response.json()["id"]

        return operation_id

    def _get_operation_status(self, operation_id: str) -> bool:
        url = f"{OPERATIONS_BASE_URL}/{operation_id}"

        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()["done"]

    def _get_recognition(self, operation_id: str) -> Any:
        url = f"{STT_BASE_URL}/getRecognition"
        params = {"operation_id": operation_id}

        response = requests.get(
            url, headers=self.headers, params=params, timeout=10, stream=True
        )
        response.raise_for_status()

        results = []
        for line in response.iter_lines():
            if line:
                try:
                    result = json.loads(line)
                    if "result" in result and "final" in result["result"]:
                        results.append(result)
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON: %s", e)
                    continue

        return results

    def _parse_results(self, raw: list) -> TranscriptionResult:
        """Преобразует JSON-результат в TranscriptionResult"""
        parsed: TranscriptionResult = SegmentCollection()

        for chunk in raw:
            if "result" not in chunk or "final" not in chunk["result"]:
                continue

            final = chunk["result"]["final"]
            if "alternatives" not in final:
                continue

            for alternative in final["alternatives"]:
                if not all(
                    key in alternative for key in ["text", "startTimeMs", "endTimeMs"]
                ):
                    continue

                if not alternative["text"]:
                    continue

                # Конвертируем миллисекунды в секунды
                start_time = timedelta(milliseconds=float(alternative["startTimeMs"]))
                end_time = timedelta(milliseconds=float(alternative["endTimeMs"]))

                # Получаем speaker, если он есть
                speaker = alternative.get("speaker", None)

                # Создаем результат распознавания
                result = TranscriptionSegment(
                    start_time, end_time, alternative["text"], speaker
                )
                print(result)
                parsed.append(result)

        return parsed
