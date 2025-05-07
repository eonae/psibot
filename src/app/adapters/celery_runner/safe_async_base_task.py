import asyncio
import logging
from abc import abstractmethod
from typing import Coroutine
from celery import Task  # type: ignore

import nest_asyncio  # type: ignore

nest_asyncio.apply()

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
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine)

    @abstractmethod
    async def run_async(self, *args, **kwargs):
        """Асинхронная логика задачи"""
        raise NotImplementedError("Subclasses must implement this method")
