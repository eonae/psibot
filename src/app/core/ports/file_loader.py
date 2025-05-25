from typing import Protocol, Tuple


class FileLoader(Protocol):
    def is_valid_file_id(self, file_id: str) -> bool:
        ...

    def load(self, file_id: str) -> Tuple[bytes, str | None]:
        ...
