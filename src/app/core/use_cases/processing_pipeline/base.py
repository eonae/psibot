from uuid import UUID

from src.app.core.ports import JobsRepository, Notifier, TasksScheduler


class BaseStageResultHandler:
    def __init__(
        self,
        jobs_repository: JobsRepository,
        tasks_scheduler: TasksScheduler,
        notifier: Notifier,
    ):
        self.jobs_repository = jobs_repository
        self.tasks_scheduler = tasks_scheduler
        self.notifier = notifier

    async def execute(self, job_id: UUID, error: Exception | None) -> None:
        job = await self.jobs_repository.get_one(job_id)
        if not job:
            raise ValueError(f"Job id={job_id} not found")

        if not job.status == self.expected_status:
            raise ValueError(f"Job id={job_id} is incorrect status for {self.stage_name}")

        if error is not None:
            job.set_failed(error)
            await self.jobs_repository.save(job)
            await self.notify_failed(job)
            raise error

        job.to_stage(self.next_status)
        await self.schedule_next(job)
        await self.jobs_repository.save(job)
        await self.notify_completed(job)

    @property
    def expected_status(self):
        raise NotImplementedError

    @property
    def next_status(self):
        raise NotImplementedError

    @property
    def stage_name(self):
        return self.__class__.__name__

    async def schedule_next(self, job):
        raise NotImplementedError

    async def notify_failed(self, job):
        raise NotImplementedError

    async def notify_completed(self, job):
        raise NotImplementedError
