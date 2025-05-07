from redis.asyncio import Redis
from src.app.config import Config

from .jobs_repository import RedisJobsRepository

config = Config()
client = Redis.from_url(config.CELERY_BROKER_URL)
jobs_repository = RedisJobsRepository(client)

__all__ = ["jobs_repository"]
