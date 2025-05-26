from datetime import timedelta

from src.app.core.models.segments.segment_collection import SegmentCollection

from .segment_base import Segment


class TranscriptionSegmentWithSpeaker(Segment):
    """Результат распознавания с указанием спикера"""

    speaker: str

    def __init__(self, start: timedelta, end: timedelta, speaker: str, text: str):
        super().__init__(start=start, end=end, speaker=speaker, text=text)

    @classmethod
    def from_segment(cls, segment: Segment) -> "TranscriptionSegmentWithSpeaker":
        if not segment.text:
            raise ValueError("Text is required in TranscriptionResultWithSpeaker")

        if not segment.speaker:
            raise ValueError("Speaker is required in TranscriptionResultWithSpeaker")

        return TranscriptionSegmentWithSpeaker(
            start=segment.start,
            end=segment.end,
            text=segment.text,
            speaker=segment.speaker,
        )


MergedTranscriptionResult = SegmentCollection[TranscriptionSegmentWithSpeaker]
