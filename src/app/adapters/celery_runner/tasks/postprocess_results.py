from uuid import UUID

from src.app.adapters.celery_runner.safe_async_base_task import SafeAsyncTask
from src.app.adapters.db.singleton import jobs_repository
from src.app.adapters.files.singleton import storage
from src.app.adapters.ml.yandex_gpt.yandex_gpt import YandexGPT
from src.app.adapters.telegram import TelegramNotifier
from src.app.adapters.telegram.singleton import bot
from src.app.config import Config
from src.app.core.services import PostprocessingService
from src.app.core.use_cases import HandlePostprocessingUseCase


class PostprocessResultsTask(SafeAsyncTask):
    name = "postprocess"

    async def run_async(self, *args, **kwargs) -> str:
        """Постпроцессинг результатов распознавания

        Args:
            args: Позиционные аргументы, первый из которых - job_id
            kwargs: Именованные аргументы

        Returns:
            job_id: ID задачи
        """

        config = Config()
        gpt = YandexGPT(
            api_key=config.YC_API_KEY,
            folder_id=config.YC_FOLDER_ID,
        )
        use_case = HandlePostprocessingUseCase(
            jobs_repository=jobs_repository,
            postprocessor=PostprocessingService(storage, gpt),
            notifier=TelegramNotifier(bot),
            storage=storage,
        )

        job_id = args[0]

        await use_case.execute(UUID(job_id))

        return job_id
