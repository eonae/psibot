from datetime import timedelta

from src.app.core.models.segments.segment_collection import SegmentCollection

from .segment_base import Segment
from .segment_transcription_with_speaker import TranscriptionSegmentWithSpeaker


class TranscriptionSegment(Segment):
    text: str

    """Результат распознавания"""

    def __init__(
        self, start: timedelta, end: timedelta, text: str, speaker: str | None = None
    ):
        super().__init__(start=start, end=end, speaker=speaker, text=text)

    def with_speaker(self, speaker: str) -> TranscriptionSegmentWithSpeaker:
        return TranscriptionSegmentWithSpeaker(
            start=self.start, end=self.end, speaker=speaker, text=self.text
        )

    @classmethod
    def from_segment(cls, segment: Segment) -> "TranscriptionSegment":
        if not segment.text:
            raise ValueError("Text is required in RecognitionResult")

        return TranscriptionSegment(
            start=segment.start,
            end=segment.end,
            text=segment.text,
            speaker=segment.speaker,
        )


TranscriptionResult = SegmentCollection[TranscriptionSegment]
