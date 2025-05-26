"""
Входная точка для запуска celery worker'а.

Запуск:

    poetry run worker worker_1
    poetry run worker worker_2

    poetry run worker --help
"""

import argparse
import subprocess


def parse_args():
    """
    Парсинг аргументов командной строки.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("worker_id", help="Worker ID")
    return parser.parse_args()


def main():
    """
    Запуск celery worker'а.
    """
    args = parse_args()
    subprocess.run(
        [
            "celery",
            "-A",
            "src.app.adapters.celery_runner.singleton",
            "worker",
            "-l",
            "DEBUG",
            # Текущая реализация нормально работает только с solo.
            # С тредами возникают конфликты asyncio (из-за aiohttp,
            # который используется в aiogram)
            # С prefork - какая-то фигня с задачей диаризации - torch видимо
            # не может в дочернем потоке работать и воркер тупо падает
            # с WorkerLostError
            "--pool=solo",
            f"--hostname={args.worker_id}@%h",
        ],
        check=True,
    )
