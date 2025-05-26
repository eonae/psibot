"""Модели данных"""

from .input_file_dto import InputFileDTO
from .segments import (
    DiarizationResult,
    DiarizationSegment,
    MergedTranscriptionResult,
    Segment,
    SegmentCollection,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionSegmentWithSpeaker,
)
from .transcription_job import Files, TranscriptionJob
from .transcription_job_status import JobStatus

__all__ = [
    "Files",
    "JobStatus",
    "TranscriptionJob",
    "InputFileDTO",
    "Segment",
    "SegmentCollection",
    "DiarizationSegment",
    "TranscriptionSegment",
    "TranscriptionSegmentWithSpeaker",
    "MergedTranscriptionResult",
    "DiarizationResult",
    "TranscriptionResult",
]
