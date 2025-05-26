"""Модель данных для результатов распознавания, диаризации и т. д."""

from .segment_base import Segment
from .segment_collection import SegmentCollection
from .segment_diarization import DiarizationResult, DiarizationSegment
from .segment_transcription import TranscriptionResult, TranscriptionSegment
from .segment_transcription_with_speaker import (
    MergedTranscriptionResult,
    TranscriptionSegmentWithSpeaker,
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
