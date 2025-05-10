from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from uuid import UUID, uuid4

from .transcription_job_status import JobStatus

logger = logging.getLogger(__name__)


@dataclass
class Files:
    original: Path
    wav: Path
    diarization: Path
    transcription: Path
    merged: Path
    postprocessed: Path


class TranscriptionJob:
    id: UUID
    user_id: int
    file_id: str
    original_filename: str | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    files: Files

    _error: str | None = None

    def __init__(self, user_id: int, file_id: str, original_filename: str | None):
        self.user_id = user_id
        self.file_id = file_id
        self.original_filename = original_filename
        self.status = JobStatus.DOWNLOADING

        self.id = uuid4()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        base_path = Path(f"{int(self.created_at.timestamp())}_{self.id}")

        self.files = Files(
            original=base_path / f"original_{self.original_filename or 'file'}",
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

    def to_processing(self, filename: str | None = None) -> None:
        self._transition(JobStatus.DOWNLOADING, JobStatus.PROCESSING)

        if not self.original_filename:
            self.original_filename = Path(filename or f"{uuid4()}.maybe_audio").name

        elif filename and self.original_filename != filename:
            logger.warning(
                "File name mismatch: %s != %s (from content-disposition)",
                self.original_filename,
                filename,
            )

    def to_postprocessing(self) -> None:
        self._transition(JobStatus.PROCESSING, JobStatus.POSTPROCESSING)

    def to_confirmation(self) -> None:
        self._transition(JobStatus.POSTPROCESSING, JobStatus.PENDING_CONFIRMATION)

    def set_confirmed(self):
        self._transition(JobStatus.PENDING_CONFIRMATION, JobStatus.CONFIRMED)

    def set_rejected(self):
        self._transition(JobStatus.PENDING_CONFIRMATION, JobStatus.REJECTED)

    def assert_is_processing(self) -> None:
        if not self.status == JobStatus.PROCESSING:
            raise ValueError(f"Job id={self.id} is not in processing status")

    def set_failed(self, error: Exception):
        if not self.is_active():
            raise ValueError(f"Job id={self.id} is not in active status")

        self.status = JobStatus.FAILED
        self._error = str(error)
        self.updated_at = datetime.now()

    def _transition(self, status_from: JobStatus, status_to: JobStatus) -> None:
        if self.status != status_from:
            raise ValueError(
                f"Job id={self.id} is can't transition to {status_to}\n"
                f"expected current status <{status_from}>, got <{self.status}>"
            )

        self.status = status_to
        self.updated_at = datetime.now()
