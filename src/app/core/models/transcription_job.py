from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from .transcription_job_status import JobStatus


@dataclass
class Files:
    wav: Path
    diarization: Path
    transcription: Path
    merged: Path
    postprocessed: Path


class TranscriptionJob:
    id: UUID
    user_id: int
    file_id: str
    original_filename: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    files: Files

    _error: str | None = None

    def __init__(self, user_id: int, file_id: str, original_filename: str):
        self.user_id = user_id
        self.file_id = file_id
        self.original_filename = original_filename
        self.status = JobStatus.DOWNLOADING

        self.id = uuid4()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        base_path = Path(f"{int(self.created_at.timestamp())}_{self.id}")

        self.files = Files(
            wav=base_path / "converted.wav",
            diarization=base_path / "diarization.txt",
            transcription=base_path / "transcription.txt",
            merged=base_path / "merged.txt",
            postprocessed=base_path / "postprocessed.txt",
        )

    def is_active(self) -> bool:
        return self.status not in [
            JobStatus.FAILED,
            JobStatus.CONFIRMED,
            JobStatus.REJECTED,
        ]

    def to_stage(self, status: JobStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()

    def set_confirmed(self):
        self.status = JobStatus.CONFIRMED
        self.updated_at = datetime.now()

    def set_rejected(self):
        self.status = JobStatus.REJECTED
        self.updated_at = datetime.now()

    def set_failed(self, error: Exception):
        self.status = JobStatus.FAILED
        self._error = str(error)
        self.updated_at = datetime.now()
