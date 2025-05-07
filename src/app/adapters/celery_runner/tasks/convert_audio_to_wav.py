from uuid import UUID

from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.services.conversion_service import ConversionService
from src.app.core.use_cases import HandleConvertUseCase


class ConvertAudioToWavTask(SafeAsyncTask):
    name = "convert"

    async def run_async(self, *args, **kwargs) -> str:
        """Обработчик успешного завершения загрузки аудио

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """
        job_id = args[0]

        use_case = HandleConvertUseCase(
            jobs_repository=make_jobs_repository(),
            converter=ConversionService(storage),
            notifier=TelegramNotifier(bot),
        )

        await use_case.execute(UUID(job_id))

        return job_id
