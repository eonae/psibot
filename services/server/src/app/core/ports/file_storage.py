"""
Интерфейс для работы с файловым хранилищем.
"""

from pathlib import Path
from typing import Protocol


class FileStorage(Protocol):
    """
    Интерфейс для работы с файловым хранилищем.
    """

    def exists(self, filename: Path) -> bool:  # type: ignore
        """Проверяет существование файла в хранилище."""

    def read(self, filename: Path) -> bytes:  # type: ignore
        """Читает файл из хранилища."""

    def save(self, file: bytes, filename: Path) -> None:  # type: ignore
        """Сохраняет файл в хранилище."""

    def copy(self, source_filename: Path, target_filename: Path) -> None:  # type: ignore
        """Копирует файл внутри хранилища."""

    def remove(self, filename: Path) -> bool:  # type: ignore
        """Удаляет файл из хранилища."""
