"""
Интерфейс для запуска пайплайна обработки.
"""

from typing import Protocol
from uuid import UUID


class PipelineRunner(Protocol):
    """
    Интерфейс для запуска пайплайна обработки.
    """

    def run_pipeline(self, job_id: UUID, should_download: bool) -> None:  # type: ignore
        """Запускает пайплайн обработки по ID задачи."""
