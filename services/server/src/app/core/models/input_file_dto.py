# app/domain/dto.py

from dataclasses import dataclass


@dataclass
class InputFileDTO:
    """Базовые характеристики файла"""

    mime_type: str | None
    size: int | None
    filename: str | None


@dataclass
class TelegramFileDTO(InputFileDTO):
    """Файл, который можно загрузить"""

    file_id: str


@dataclass
class DownloadableFileDTO(InputFileDTO):
    """Файл, который можно загрузить"""

    url: str


@dataclass
class DownloadedFileDTO(InputFileDTO):
    """Файл, который был загружен"""

    content: bytes
