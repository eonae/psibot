from typing import Protocol
from uuid import UUID


class TasksScheduler(Protocol):
    def schedule(self, task_name: str, job_id: UUID, **kwargs) -> None:
        ...
