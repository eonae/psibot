from typing import Protocol


class FileLoader(Protocol):
    def load(self, file_id: str) -> bytes:
        ...
