import json
import logging
import asyncio
from typing import Any, Callable, Dict, Awaitable

from celery import Task  # type: ignore
from celery.result import AsyncResult  # type: ignore
from redis.asyncio import Redis  # type: ignore
from redis.asyncio.client import PubSub  # type: ignore


logger = logging.getLogger(__name__)

REDIS_CHANNEL_COMPLETED = 'celery_task_completed'

Headers = Dict[str, str]
AsyncCallback = Callable[[Exception | None, Any | None, Headers], Awaitable[None]]


class ReactiveResults:
    def __init__(self, redis: Redis):
        self.redis = redis
        self._callbacks: Dict[str, AsyncCallback] = {}
        self._default_callback: AsyncCallback | None = None
        self._pubsub: PubSub | None = None
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Запустить прослушивание канала Redis"""
        if self._task is not None:
            return

        logger.info("Starting celery results listener...")

        self._running = True
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(REDIS_CHANNEL_COMPLETED)
        self._pubsub = pubsub

        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Остановить прослушивание канала Redis"""
        self._running = False
        if self._task is not None:
            await self._task
            self._task = None

        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

    def subscribe(
        self,
        task_name: str,
        callback: AsyncCallback,
    ) -> None:
        """Подписаться на уведомления о конкретной задаче

        Args:
            task_name: Имя задачи
            callback: Асинхронная функция обратного вызова, принимающая словарь с данными задачи
        """
        self._callbacks[task_name] = callback

    async def publish(self, task: Task) -> None:
        """Опубликовать результат задачи

        Args:
            task: Объект задачи celery
        """
        data = json.dumps((task.request.id, task.name, task.request.headers))
        print(f"🔗🔗🔗 Publishing data: {data}")
        await self.redis.publish(REDIS_CHANNEL_COMPLETED, data)

    def set_default_callback(self, callback: AsyncCallback) -> None:
        """Установить обработчик по умолчанию для неизвестных задач

        Args:
            callback: Асинхронная функция обратного вызова, принимающая словарь с данными задачи
        """
        self._default_callback = callback

    async def _run(self) -> None:
        """Асинхронный цикл обработки сообщений"""
        assert self._pubsub is not None
        while self._running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True)
                if message is None:
                    await asyncio.sleep(0.1)
                    continue

                await self._process_message(message)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error in message processing loop: %s", e)
                await asyncio.sleep(1)  # Пауза перед повторной попыткой

    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Обработка сообщения из Redis

        Args:
            message: Сообщение из Redis
        """
        try:
            task_id, task_name, headers = json.loads(message["data"].decode())
            callback = self._callbacks.get(task_name) or self._default_callback

            if callback:
                result = AsyncResult(task_id).result
                if isinstance(result, Exception):
                    await callback(result, None, headers)
                else:
                    await callback(None, result, headers)
            else:
                logger.warning("No callback for task %s", task_name)

        except json.JSONDecodeError as e:
            logger.error("Failed parse json: %s", e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to process message: %s", e)
