import logging

from src.app.core.ports import JobsRepository, Notifier, MessageType

logger = logging.getLogger(__name__)


class HandleRejectionUseCase:
    def __init__(
        self,
        jobs: JobsRepository,
        notifier: Notifier,
    ) -> None:
        self.jobs_repository = jobs
        self.notifier = notifier

    async def execute(self, user_id: int) -> None:
        """Обрабатывает отклонение результатов транскрибации.

        Args:
            user_id: ID пользователя
        """
        logger.info("Handling rejection for user %s", user_id)

        # Получаем последнюю задачу пользователя
        job = await self.jobs_repository.get_for_user_active(user_id)
        if not job:
            logger.error("No job found for user %d", user_id)
            await self.notifier.notify(user_id, MessageType.NO_JOBS)
            return

        if job.status != "pending_confirmation":
            logger.error("Job %s is not in pending_confirmation status", job.id)
            await self.notifier.notify(user_id, MessageType.JOB_WRONG_STATUS)
            return

        # Обновляем статус задачи
        job.set_failed(Exception("User rejected the result"))
        await self.jobs_repository.save(job)

        # Отправляем уведомление пользователю
        await self.notifier.notify(user_id, MessageType.REJECTED)

        logger.info("Rejection handled for job %s", job.id)
