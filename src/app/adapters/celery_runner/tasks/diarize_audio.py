from uuid import UUID

from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.ml import PyannoteDiarizer
from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram import TelegramNotifier
from src.app.config import Config
from src.app.core.services import DiarizationService
from src.app.core.use_cases import HandleDiarizeUseCase

diarizer = PyannoteDiarizer.from_config(Config())


class DiarizeAudioTask(SafeAsyncTask):
    name = "diarize"

    async def run_async(self, *args, **kwargs) -> str:
        """Определяет спикеров на аудиозаписи и сохраняет результат в хранилище

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """
        job_id = args[0]

        use_case = HandleDiarizeUseCase(
            jobs_repository=make_jobs_repository(),
            diarizer=DiarizationService(storage, diarizer),
            notifier=TelegramNotifier(bot),
        )

        await use_case.execute(UUID(job_id))

        return job_id
