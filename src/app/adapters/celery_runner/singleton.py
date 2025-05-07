import asyncio
import logging
from celery import Celery  # type: ignore
from celery.signals import worker_process_init, worker_ready  # type: ignore

from src.app.adapters.celery_runner.tasks import (
    ConvertAudioToWavTask,
    DiarizeAudioTask,
    DownloadAudioTask,
    MergeResultsTask,
    PostprocessResultsTask,
    TranscribeAudioTask,
)

from src.app.config import Config

logger = logging.getLogger(__name__)

config = Config()

celery_app = Celery(
    "speechkit",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
)

celery_app.register_task(DownloadAudioTask())
celery_app.register_task(ConvertAudioToWavTask())
celery_app.register_task(DiarizeAudioTask())
celery_app.register_task(TranscribeAudioTask())
celery_app.register_task(MergeResultsTask())
celery_app.register_task(PostprocessResultsTask())

print("Registered tasks: %s", list(celery_app.tasks.keys()))

celery_app.conf.update(
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


@worker_ready.connect
@worker_process_init.connect
def init_worker_loop(**_):
    print("INITIALIZE WORKER LOOP")
    try:
        loop = asyncio.get_running_loop()
        print(f"Found existing event loop: {loop}")
    except RuntimeError:
        print("Creating new event loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(f"Created and set new event loop: {loop}")
