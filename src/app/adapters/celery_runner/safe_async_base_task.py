# infrastructure/tasks/async_task_base.py

import asyncio
import logging
from abc import abstractmethod
from typing import Coroutine
from celery import Task  # type: ignore

logger = logging.getLogger(__name__)


class SafeAsyncTask(Task):
    """Базовый класс для async Celery-задач.
    Потомки реализуют async def run_async(...), а не run(...).
    """

    soft_retry = True  # включить или выключить retry

    def run(self, *args, **kwargs):
        """Синхронный вход, вызываемый Celery — исполняет async run_async"""
        try:
            coroutine = self.run_async(*args, **kwargs)
            return self._execute_async(coroutine)
        except Exception as exc:
            logger.exception("[%s] Error executing task", self.name)
            if self.soft_retry:
                raise self.retry(exc=exc, countdown=5)
            raise

    def _execute_async(self, coroutine: Coroutine):
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                logger.warning(
                    "[%s] Active event loop, using run_until_complete (may hang)",
                    self.name,
                )
            return loop.run_until_complete(coroutine)
        except RuntimeError:
            return asyncio.run(coroutine)

    @abstractmethod
    async def run_async(self, *args, **kwargs):
        """Асинхронная логика задачи"""
        raise NotImplementedError("Subclasses must implement this method")
