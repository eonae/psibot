from redis.asyncio import Redis
from src.app.config import Config

from .jobs_repository import RedisJobsRepository


def make_jobs_repository():
    config = Config()
    client = Redis.from_url(config.CELERY_BROKER_URL)

    return RedisJobsRepository(client)
