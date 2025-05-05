"""Модель данных для результатов распознавания, диаризации и т. д."""

from .segment_base import Segment
from .segment_collection import SegmentCollection
from .segment_diarization import DiarizationSegment, DiarizationResult
from .segment_transcription import TranscriptionSegment, TranscriptionResult
from .segment_transcription_with_speaker import (
    TranscriptionSegmentWithSpeaker,
    MergedTranscriptionResult,
)

__all__ = [
    "Segment",
    "SegmentCollection",
    "DiarizationSegment",
    "DiarizationResult",
    "TranscriptionSegment",
    "TranscriptionResult",
    "TranscriptionSegmentWithSpeaker",
    "MergedTranscriptionResult",
]
