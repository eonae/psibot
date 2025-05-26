"""
Обработчик подтверждения результатов транскрибации.
"""

import logging

from src.app.core.models import JobStatus
from src.app.core.ports import FileStorage, JobsRepository, MessageType, Notifier

logger = logging.getLogger(__name__)


class HandleConfirmationUseCase:
    """
    Обработчик подтверждения результатов транскрибации.
    """

    def __init__(
        self,
        jobs: JobsRepository,
        file_storage: FileStorage,
        notifier: Notifier,
    ) -> None:
        self.job_repository = jobs
        self.file_storage = file_storage
        self.notifier = notifier

    async def execute(self, user_id: int) -> None:
        """Обрабатывает подтверждение результатов транскрибации.

        Args:
            user_id: ID пользователя
        """

        logger.info("Handling confirmation for user %s", user_id)

        # Получаем последнюю задачу пользователя
        job = await self.job_repository.get_for_user_one(user_id)
        if not job:
            logger.error("No job found for user %d", user_id)
            await self.notifier.notify(user_id, MessageType.NO_JOBS)
            return

        if job.status != JobStatus.PENDING_CONFIRMATION:
            logger.error("Job %s is not in pending_confirmation status", job.id)
            await self.notifier.notify(user_id, MessageType.JOB_WRONG_STATUS)
            return

        # Обновляем статус задачи
        job.set_confirmed()
        await self.job_repository.save(job)

        # Отправляем уведомление пользователю
        await self.notifier.notify(user_id, MessageType.CONFIRMED)

        logger.info("Confirmation handled for job %s", job.id)
