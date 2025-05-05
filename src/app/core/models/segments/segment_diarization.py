"""Основной модуль приложения"""

import logging
from datetime import timedelta

from .segment_collection import SegmentCollection

from .segment_base import Segment

logger = logging.getLogger(__name__)


class DiarizationSegment(Segment):
    """Результат диаризации"""

    speaker: str
    text: None

    def __init__(self, start: timedelta, end: timedelta, speaker: str):
        super().__init__(start=start, end=end, speaker=speaker)

    @classmethod
    def from_segment(cls, segment: Segment) -> "DiarizationSegment":
        if not segment.speaker:
            raise ValueError("Speaker is required in DiarizationResult")

        return cls(
            start=segment.start,
            end=segment.end,
            speaker=segment.speaker,
        )


DiarizationResult = SegmentCollection[DiarizationSegment]
