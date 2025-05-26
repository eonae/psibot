"""
Интерфейс для загрузки файлов из источника.
"""

from typing import Protocol, Tuple


class FileLoader(Protocol):
    """
    Интерфейс для загрузки файлов из источника.
    """

    def is_valid_file_id(self, file_id: str) -> bool:  # type: ignore
        """Проверяет, является ли file_id валидным."""

    def load(self, file_id: str) -> Tuple[bytes, str | None]:  # type: ignore
        """Загружает файл из источника."""
