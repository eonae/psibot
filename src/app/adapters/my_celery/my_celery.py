import asyncio
from uuid import UUID

from celery import Celery, Task  # type: ignore
from celery.signals import task_failure, task_success  # type: ignore
from lib.celery_reactive import ReactiveResults
from lib.celery_reactive.reactive_results import AsyncCallback
from src.app.core.ports import TasksScheduler


class MyCelery(Celery, TasksScheduler):
    reactive_results: ReactiveResults | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conf.update(
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

    def connect_reactive_results(self, results: ReactiveResults):
        self.reactive_results = results

    def configure_signals(self):
        print("🔗🔗🔗 Configuring signals")
        results = self.reactive_results
        if results is None:
            raise ValueError("Reactive results are not connected")

        def notify_task_result(sender: Task, **_):
            print("🔗🔗🔗 Notifying task result")
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(results.publish(sender))
            else:
                loop.run_until_complete(results.publish(sender))

        print("🔗🔗🔗 Connecting task_success and task_failure")
        task_success.connect(notify_task_result)
        task_failure.connect(notify_task_result)

    def schedule(self, task_name: str, job_id: UUID, **kwargs) -> None:
        task = self.tasks[task_name]
        task.apply_async(kwargs=kwargs, headers={"job_id": str(job_id)})

    def subscribe(self, task_name: str, handler: AsyncCallback):
        if self.reactive_results is None:
            raise ValueError("Reactive results are not connected")

        self.reactive_results.subscribe(task_name, handler)

    def listen_results(self):
        if self.reactive_results is None:
            raise ValueError("Reactive results are not connected")

        return self.reactive_results.start()

    def stop_listening_results(self):
        if self.reactive_results is None:
            raise ValueError("Reactive results are not connected")

        return self.reactive_results.stop()
