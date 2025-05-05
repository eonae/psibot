from pathlib import Path
from typing import Protocol


class FileStorage(Protocol):
    def exists(self, filename: Path) -> bool:
        ...

    def read(self, filename: Path) -> bytes:
        ...

    def save(self, file: bytes, filename: Path) -> None:
        ...

    def copy(self, source_filename: Path, target_filename: Path) -> None:
        ...

    def remove(self, filename: Path) -> bool:
        ...
