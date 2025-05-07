from uuid import UUID

from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask
from src.app.adapters.db.singleton import jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.ml import YandexSpeechKit
from src.app.adapters.s3bucket import S3Bucket
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.config import Config
from src.app.core.services import TranscriptionService
from src.app.core.use_cases import HandleTranscriptionUseCase


class TranscribeAudioTask(SafeAsyncTask):
    name = "transcribe"

    async def run_async(self, *args, **kwargs) -> str:
        """Распознает аудиофайл и сохраняет результат в хранилище

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """

        config = Config()
        stt = YandexSpeechKit(
            api_key=config.YC_API_KEY,
            bucket=S3Bucket(config),
        )

        use_case = HandleTranscriptionUseCase(
            jobs_repository=jobs_repository,
            transcriber=TranscriptionService(storage, stt),
            notifier=TelegramNotifier(bot),
        )

        job_id = args[0]

        await use_case.execute(UUID(job_id))

        return job_id
