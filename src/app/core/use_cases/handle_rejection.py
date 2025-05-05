import logging

from src.app.core.ports import JobsRepository, Responder

logger = logging.getLogger(__name__)


class HandleRejectionUseCase:
    def __init__(
        self,
        job_repository: JobsRepository,
        responder: Responder,
    ) -> None:
        self.job_repository = job_repository
        self.responder = responder

    async def execute(self, user_id: int) -> None:
        """Обрабатывает отклонение результатов транскрибации.

        Args:
            user_id: ID пользователя
        """
        logger.info("Handling rejection for user %s", user_id)

        # Получаем последнюю задачу пользователя
        job = await self.job_repository.get_for_user_active(user_id)
        if not job:
            logger.error("No job found for user %d", user_id)
            await self.responder.reply_no_jobs()
            return

        if job.status != "pending_confirmation":
            logger.error("Job %s is not in pending_confirmation status", job.id)
            await self.responder.reply_job_wrong_status()
            return

        # Обновляем статус задачи
        job.set_failed(Exception("User rejected the result"))
        await self.job_repository.save(job)

        # Отправляем уведомление пользователю
        await self.responder.reply_rejected()

        logger.info("Rejection handled for job %s", job.id)
