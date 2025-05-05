from uuid import UUID

from src.app.core.models.transcription_job import TranscriptionJob
from src.app.core.ports.jobs_repository import JobsRepository


class InMemoryJobsRepository(JobsRepository):
    jobs: dict[UUID, TranscriptionJob]

    def __init__(self):
        self.jobs = {}

    async def get_for_user_active(self, user_id: int) -> TranscriptionJob | None:
        return next(
            (
                job
                for job in self.jobs.values()
                if job.user_id == user_id and job.is_active()
            ),
            None,
        )

    async def get_for_user_many(self, user_id: int) -> list[TranscriptionJob]:
        return [job for job in self.jobs.values() if job.user_id == user_id]

    async def get_one(self, job_id: UUID) -> TranscriptionJob:
        return self.jobs[job_id]

    async def save(self, job: TranscriptionJob) -> TranscriptionJob:
        self.jobs[job.id] = job
        return job
