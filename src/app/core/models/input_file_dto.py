# app/domain/dto.py

from dataclasses import dataclass


@dataclass
class InputFileDTO:
    file_id: str
    mime_type: str | None
    size: int | None
    filename: str | None
