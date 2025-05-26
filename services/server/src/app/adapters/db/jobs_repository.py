"""
Реализация JobsRepository на основе Redis.
"""

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from redis.asyncio import Redis  # type: ignore
from src.app.core.models import Files, JobStatus, TranscriptionJob
from src.app.core.ports import JobsRepository


class RedisJobsRepository(JobsRepository):
    """Реализация JobsRepository на основе Redis."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.key_prefix = "transcription_job:"

    async def get_for_user_one(self, user_id: int) -> TranscriptionJob | None:
        user_key = self._get_user_key(user_id)
        job_ids = await self.redis.smembers(user_key)

        for job_id in job_ids:
            job = await self.get_one(UUID(job_id.decode()))
            if job.is_active():
                return job
        return None

    async def get_for_user_many(self, user_id: int) -> list[TranscriptionJob]:
        user_key = self._get_user_key(user_id)
        job_ids = await self.redis.smembers(user_key)

        jobs = []
        for job_id in job_ids:
            try:
                job = await self.get_one(UUID(job_id.decode()))
                jobs.append(job)
            except KeyError:
                # Если job не найден, пропускаем его
                continue
        return jobs

    async def get_one(self, job_id: UUID) -> TranscriptionJob:
        key = self._get_key(job_id)
        data = await self.redis.get(key)
        if not data:
            raise KeyError(f"Job {job_id} not found")

        return self._deserialize_job(data)

    async def save(self, job: TranscriptionJob) -> TranscriptionJob:
        key = self._get_key(job.id)
        user_key = self._get_user_key(job.user_id)

        # Сохраняем job
        await self.redis.set(key, self._serialize_job(job))

        # Добавляем job в множество jobs пользователя
        await self.redis.sadd(user_key, str(job.id))

        return job

    def _get_key(self, job_id: UUID) -> str:
        return f"{self.key_prefix}{str(job_id)}"

    def _get_user_key(self, user_id: int) -> str:
        return f"{self.key_prefix}user:{user_id}"

    def _serialize_job(self, job: TranscriptionJob) -> str:
        return json.dumps(
            {
                "id": str(job.id),
                "user_id": job.user_id,
                "file_id": job.file_id,
                "original_filename": job.original_filename,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
                "files": {
                    "original": str(job.files.original),
                    "wav": str(job.files.wav),
                    "diarization": str(job.files.diarization),
                    "transcription": str(job.files.transcription),
                    "merged": str(job.files.merged),
                    "postprocessed": str(job.files.postprocessed),
                },
                "error": job._error,  # pylint: disable=protected-access
            }
        )

    def _deserialize_job(self, data: str) -> TranscriptionJob:
        job_data = json.loads(data)

        # Создаем базовый объект
        job = TranscriptionJob(
            user_id=job_data["user_id"],
            file_id=job_data["file_id"],
            original_filename=job_data["original_filename"],
        )

        # Восстанавливаем остальные поля
        job.id = UUID(job_data["id"])
        job.status = JobStatus(job_data["status"])
        job.created_at = datetime.fromisoformat(job_data["created_at"])
        job.updated_at = datetime.fromisoformat(job_data["updated_at"])
        job.files = Files(
            original=Path(job_data["files"]["original"]),
            wav=Path(job_data["files"]["wav"]),
            diarization=Path(job_data["files"]["diarization"]),
            transcription=Path(job_data["files"]["transcription"]),
            merged=Path(job_data["files"]["merged"]),
            postprocessed=Path(job_data["files"]["postprocessed"]),
        )

        job._error = job_data.get("error")  # pylint: disable=protected-access

        return job
