from uuid import UUID

from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask
from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.core.services import MergingService
from src.app.core.use_cases import HandleMergingUseCase


class MergeResultsTask(SafeAsyncTask):
    name = "merge"

    async def run_async(self, *args, **kwargs) -> str:
        """Сливает результаты диаризации и распознавания

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """
        job_id, _ = args[0]

        use_case = HandleMergingUseCase(
            jobs_repository=make_jobs_repository(),
            merger=MergingService(storage),
            notifier=TelegramNotifier(bot),
        )

        await use_case.execute(UUID(job_id), self.is_last_retry())

        return job_id
