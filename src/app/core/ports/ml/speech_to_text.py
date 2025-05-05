from pathlib import Path
from typing import Protocol

from src.app.core.models import SegmentCollection, TranscriptionSegment


class SpeechToText(Protocol):
    def transcribe(self, audio_file: Path) -> SegmentCollection[TranscriptionSegment]:
        ...
