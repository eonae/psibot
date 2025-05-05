from typing import Optional, Protocol
from pathlib import Path


class Bucket(Protocol):
    def upload(
        self, path: str | Path, object_name: Optional[str] = None
    ) -> None:
        ...

    def get_presigned_url(self, object_name: str | Path) -> str:
        ...
