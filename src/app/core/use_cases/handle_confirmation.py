import logging

from src.app.core.models.transcription_job_status import JobStatus
from src.app.core.ports import FileStorage, JobsRepository, Responder

logger = logging.getLogger(__name__)


class HandleConfirmationUseCase:
    def __init__(
        self,
        job_repository: JobsRepository,
        file_storage: FileStorage,
        responder: Responder,
    ) -> None:
        self.job_repository = job_repository
        self.file_storage = file_storage
        self.responder = responder

    async def execute(self, user_id: int) -> None:
        """Обрабатывает подтверждение результатов транскрибации.

        Args:
            user_id: ID пользователя
        """

        logger.info("Handling confirmation for user %s", user_id)

        # Получаем последнюю задачу пользователя
        job = await self.job_repository.get_for_user_active(user_id)
        if not job:
            logger.error("No job found for user %d", user_id)
            await self.responder.reply_no_jobs()
            return

        if job.status != JobStatus.PENDING_CONFIRMATION:
            logger.error("Job %s is not in pending_confirmation status", job.id)
            await self.responder.reply_job_wrong_status()
            return

        # Обновляем статус задачи
        job.set_confirmed()
        await self.job_repository.save(job)

        # Отправляем уведомление пользователю
        await self.responder.reply_confirmed()

        logger.info("Confirmation handled for job %s", job.id)
