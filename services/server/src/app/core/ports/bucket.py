"""
Интерфейс для работы с сетевым файловым хранилищем.
"""

from typing import Optional, Protocol
from pathlib import Path


class Bucket(Protocol):
    """
    Интерфейс для работы с сетевым файловым хранилищем.
    """

    def upload(self, path: str | Path, object_name: Optional[str] = None) -> None:
        """Загружает файл в хранилище."""

    def get_presigned_url(self, object_name: str | Path) -> str:  # type: ignore
        """Получает presigned URL для файла."""
