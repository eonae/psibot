import asyncio
from celery import Task
from celery.signals import task_failure, task_success
from dotenv import load_dotenv
from redis.asyncio import Redis

from lib.celery_reactive import ReactiveResults
from src.app.adapters.my_celery import MyCelery
from src.app.adapters.my_celery.tasks import (
    convert_to_wav_task,
    diarize_audio_task,
    download_audio_task,
    merge_results_task,
    postprocess_results_task,
    transcribe_audio_task,
)
from src.app.config import Config

load_dotenv()

config = Config()

my_celery_app = MyCelery(
    "speechkit",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
)

_redis = Redis.from_url(config.CELERY_BROKER_URL)
results = ReactiveResults(_redis)

my_celery_app.task(diarize_audio_task, name="diarize")
my_celery_app.task(transcribe_audio_task, name="transcribe")
my_celery_app.task(merge_results_task, name="merge")
my_celery_app.task(postprocess_results_task, name="postprocess")
my_celery_app.task(convert_to_wav_task, name="convert")
my_celery_app.task(download_audio_task, name="download")

my_celery_app.connect_reactive_results(results)
# my_celery_app.configure_signals()


@task_success.connect
def notify_success(sender: Task, **_):
    print("🔗🔗🔗 Notifying task success")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(results.publish(sender))
    else:
        loop.run_until_complete(results.publish(sender))


@task_failure.connect
def notify_failure(sender: Task, **_):
    print("🔗🔗🔗 Notifying task failure")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(results.publish(sender))
    else:
        loop.run_until_complete(results.publish(sender))
