"""File loaders."""

from .google_drive_file_loader import GoogleDriveFileLoader
from .telegram_file_loader import TelegramFileLoader
from .yandex_disk_file_loader import YandexDiskFileLoader

__all__ = ["TelegramFileLoader", "YandexDiskFileLoader", "GoogleDriveFileLoader"]
