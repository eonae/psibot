from typing import Any


def task_is(task_name: str, kwargs: dict[str, Any]) -> bool:
    return kwargs.get("task_name") == task_name


class TaskResult[T: Any]:
    task_id: str
    task_name: str
    result: T

    def __init__(self, task_id: str, task_name: str, result: T):
        self.task_id = task_id
        self.task_name = task_name
        self.result = result

    def match(self, task_name: str) -> bool:
        return self.task_name == task_name

    @classmethod
    def from_kwargs(cls, kwargs: dict[str, Any]) -> "TaskResult[T]":
        task_name = kwargs.get("task_name")
        if not task_name or not isinstance(task_name, str):
            raise ValueError("Task name is required")

        task_id = kwargs.get("task_id")
        if not task_id or not isinstance(task_id, str):
            raise ValueError("Task ID is required")

        result = kwargs.get("result")
        if not result:
            raise ValueError("Result is required")

        return cls(
            task_id=task_id,
            task_name=task_name,
            result=result,
        )
