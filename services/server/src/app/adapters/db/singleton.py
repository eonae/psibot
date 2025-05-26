"""
Инициализация репозитория на основе Redis.
"""

from redis.asyncio import Redis  # type: ignore
from src.app.config import Config

from .jobs_repository import RedisJobsRepository


def make_jobs_repository():
    """
    Создаёт репозиторий для задач на основе Redis.
    """

    config = Config()
    client = Redis.from_url(config.CELERY_BROKER_URL)

    return RedisJobsRepository(client)
