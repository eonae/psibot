import asyncio

from celery import Celery, Task  # type: ignore
from celery.signals import task_success, task_failure  # type: ignore
from redis.asyncio import Redis

from lib.celery_reactive import ReactiveResults
from lib.celery_reactive.test.config import BROKER_URL, RESULT_BACKEND  # type: ignore


results = ReactiveResults(Redis.from_url(BROKER_URL))

app = Celery(
    "speechkit",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["src.test.worker.tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_publish_retry=True,
    task_ignore_result=False,
    result_expires=3600,
    task_store_errors_even_if_ignored=True,
    task_store_metadata=True,
)


@task_success.connect
def notify_task_success(sender: Task, **_):
    print("✅ Задача успешно выполнена:")
    asyncio.run(results.publish(sender))


@task_failure.connect
def notify_task_failure(sender: Task, **_):
    print("🚨 Задача завершилась с ошибкой:")
    asyncio.run(results.publish(sender))
