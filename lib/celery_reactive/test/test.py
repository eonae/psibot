import asyncio
import logging
from redis.asyncio import Redis  # type: ignore

from lib.celery_reactive import ReactiveResults, Headers
from lib.celery_reactive.test.config import BROKER_URL
from lib.celery_reactive.test.tasks import add

logging.basicConfig(level=logging.DEBUG)

results = ReactiveResults(Redis.from_url(BROKER_URL))


async def main():
    task = add.apply_async(
        args=[1, 2],
        headers={"job_id": "test_job_123"}
    )

    print(f"🚀 Задача запущена: {task.id}")

    print("\n⏳ Ожидание событий от Celery...")

    async def on_add_result(ex: Exception | None, result: int | None, headers: Headers):
        if ex:
            print("❌ Задача завершилась с ошибкой:")
            print(f"ID задачи: {headers.get('job_id')}")
            print(f"Ошибка: {ex}")
        else:
            print("✅ Задача успешно выполнена:")
            print(f"ID задачи: {headers.get('job_id')}")
            print(f"Результат: {result}")
            print(f"Хедеры: {headers}")

    results.subscribe(add.name, on_add_result)
    await results.start()

    # Держим основной поток активным, пока не получим Ctrl+C
    try:
        print("\n👉 Нажмите Ctrl+C для завершения...")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Завершение работы...")
    finally:
        await results.stop()


if __name__ == "__main__":
    asyncio.run(main())
