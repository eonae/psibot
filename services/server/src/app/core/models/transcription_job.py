"""
Модель задачи распознавания.
"""

from enum import Enum
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from .transcription_job_status import JobStatus

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """
    Тип источника файла.
    """

    DOWNLOADED_FILE_PATH = "downloaded_file_path"
    UPLOAD_URL = "upload_url"
    TELEGRAM_FILE_ID = "telegram_file_id"


@dataclass
class FileSource:
    """
    Источник файла.
    """

    type: SourceType
    value: str


@dataclass
class Paths:
    """
    Файлы, связанные с задачей распознавания.
    """

    original: Path
    wav: Path
    diarization: Path
    transcription: Path
    merged: Path
    postprocessed: Path


class TranscriptionJob:
    """
    Модель задачи распознавания.
    """

    id: UUID
    user_id: int
    source: FileSource
    original_filename: str | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    paths: Paths

    _error: str | None = None

    def __init__(self, user_id: int, source: FileSource, original_filename: str | None):
        self.user_id = user_id
        self.source = source
        self.original_filename = original_filename
        self.status = JobStatus.DOWNLOADING

        self.id = uuid4()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        base_path = Path(f"{int(self.created_at.timestamp())}_{self.id}")

        self.paths = Paths(
            original=base_path / f"original_{self.original_filename or 'file'}",
            wav=base_path / "converted.wav",
            diarization=base_path / "diarization.txt",
            transcription=base_path / "transcription.txt",
            merged=base_path / "merged.txt",
            postprocessed=base_path / "postprocessed.txt",
        )

    def is_active(self) -> bool:
        """
        Проверяет, является ли задача активной.
        """

        return self.status not in [
            JobStatus.FAILED,
            JobStatus.CONFIRMED,
            JobStatus.REJECTED,
        ]

    def to_processing(self, filename: str | None = None) -> None:
        """
        Переводит задачу в статус PROCESSING.
        """

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
        """
        Переводит задачу в статус POSTPROCESSING.
        """

        self._transition(JobStatus.PROCESSING, JobStatus.POSTPROCESSING)

    def to_confirmation(self) -> None:
        """
        Переводит задачу в статус PENDING_CONFIRMATION.
        """

        self._transition(JobStatus.POSTPROCESSING, JobStatus.PENDING_CONFIRMATION)

    def set_confirmed(self):
        """
        Переводит задачу в статус CONFIRMED.
        """

        self._transition(JobStatus.PENDING_CONFIRMATION, JobStatus.CONFIRMED)

    def set_rejected(self):
        """
        Переводит задачу в статус REJECTED.
        """

        self._transition(JobStatus.PENDING_CONFIRMATION, JobStatus.REJECTED)

    def assert_is_processing(self) -> None:
        """
        Проверяет, что задача находится в статусе PROCESSING.
        """

        if not self.status == JobStatus.PROCESSING:
            raise ValueError(f"Job id={self.id} is not in processing status")

    def set_failed(self, error: Exception):
        """
        Переводит задачу в статус FAILED.
        """

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
