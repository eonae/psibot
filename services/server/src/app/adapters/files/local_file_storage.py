"""Модуль для работы с аудио файлами

Особенности:
    - Автоматическое создание поддиректорий при сохранении файлов
    - Все пути формируются относительно базовой директории
    - Поддерживается любая глубина вложенности директорий
    - Рекурсивное удаление пустых директорий при удалении файлов

Пример:
    storage = LocalFileStorage(Path("/base/dir"))
    storage.save(file_bytes, "audio/2024/03/15/song.mp3")
    # Автоматически создаст структуру:
    # /base/dir/audio/2024/03/15/
"""

import logging
import shutil
from pathlib import Path

from src.app.core.ports import FileStorage

logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorage):
    """Хранилище файлов на локальном диске"""

    def __init__(self, base_dir: Path):
        """Инициализация файлового хранилища

        Args:
            base_dir: Базовая директория для хранения файлов
        """
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def exists(self, filename: Path) -> bool:
        """Проверяет существование файла в хранилище

        Args:
            filename: Имя файла

        Returns:
            bool: True если файл существует, False в противном случае
        """
        file_path = self.base_dir / filename
        exists = file_path.exists()
        logger.debug(
            "🔍 File %s %s", file_path, "exists" if exists else "does not exist"
        )
        return exists

    def save(self, file: bytes, filename: Path) -> None:
        """Сохраняет файл в хранилище

        Args:
            file: Содержимое файла в байтах
            filename: Имя файла
        """
        file_path = self.base_dir / filename
        # Создаем директорию для файла, если её нет
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_bytes(file)
        logger.info("✅ File saved: %s", file_path)

    def read(self, filename: Path) -> bytes:
        """Читает файл из хранилища

        Args:
            filename: Имя файла

        Returns:
            bytes: Содержимое файла

        Raises:
            FileNotFoundError: Если файл не найден
        """
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info("📖 Reading file: %s", file_path)
        return file_path.read_bytes()

    def copy(self, source_filename: Path, target_filename: Path) -> None:
        """Копирует файл внутри хранилища

        Args:
            source_filename: Имя исходного файла
            target_filename: Имя целевого файла

        Raises:
            FileNotFoundError: Если исходный файл не найден
        """
        source_path = self.base_dir / source_filename
        target_path = self.base_dir / target_filename

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Создаем директорию для целевого файла, если её нет
        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_path, target_path)
        logger.info("📋 File copied: %s -> %s", source_path, target_path)

    def remove(self, filename: Path) -> bool:
        """Удаляет файл из хранилища

        Если после удаления файла остаются пустые директории,
        они также будут удалены рекурсивно.

        Args:
            filename: Имя файла

        Returns:
            bool: True если файл удален, False в противном случае
        """
        file_path = self.base_dir / filename
        if not file_path.exists():
            return False

        # Удаляем файл
        file_path.unlink()
        logger.info("🗑️ File removed: %s", file_path)

        # Рекурсивно удаляем пустые директории
        current_dir = file_path.parent
        while current_dir != self.base_dir:
            try:
                # Пытаемся удалить директорию
                current_dir.rmdir()
                logger.debug("🗑️ Empty directory removed: %s", current_dir)
                current_dir = current_dir.parent
            except OSError:
                # Если директория не пуста или это базовая директория
                # - прекращаем
                break

        return True
