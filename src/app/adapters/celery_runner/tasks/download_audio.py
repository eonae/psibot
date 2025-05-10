from uuid import UUID

from src.app.adapters.db.singleton import make_jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.loaders import (
    GoogleDriveFileLoader,
    TelegramFileLoader,
    YandexDiskFileLoader,
)
from src.app.adapters.telegram.singleton import bot
from src.app.adapters.telegram import TelegramNotifier
from src.app.core.use_cases import HandleDownloadUseCase
from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask


class DownloadAudioTask(SafeAsyncTask):
    name = "download"

    async def run_async(self, *args, **kwargs) -> str:
        """Скачивает аудиофайл из Telegram и сохраняет в хранилище

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """
        job_id = args[0]

        use_case = HandleDownloadUseCase(
            jobs_repository=make_jobs_repository(),
            storage=storage,
            notifier=TelegramNotifier(bot),
            loaders=[
                TelegramFileLoader(),
                GoogleDriveFileLoader(),
                YandexDiskFileLoader(),
            ],
        )

        await use_case.execute(UUID(job_id), self.is_last_retry())

        return job_id
