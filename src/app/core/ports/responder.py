from typing import Protocol


class Responder(Protocol):
    async def reply_wrong_mime_type(self, mime_type: str) -> None:
        ...

    async def reply_file_size_missing(self) -> None:
        ...

    async def reply_file_size_too_large(self, max_size: int, size: int) -> None:
        ...

    async def reply_file_is_downloading(self) -> None:
        ...

    async def reply_confirmed(self) -> None:
        ...

    async def reply_rejected(self) -> None:
        ...

    async def reply_no_jobs(self) -> None:
        ...

    async def reply_job_wrong_status(self) -> None:
        ...
