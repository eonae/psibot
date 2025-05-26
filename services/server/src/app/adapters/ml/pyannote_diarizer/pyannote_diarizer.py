from datetime import timedelta
from pathlib import Path
from typing import Any, List

from pyannote.audio import Pipeline  # type: ignore

from src.app.config import Config
from src.app.core.models.segments import (
    DiarizationResult,
    DiarizationSegment,
    SegmentCollection,
)
from src.app.core.ports.ml.diarizer import Diarizer
from src.shared.hugging_face import create_pipeline
from src.shared.logging import log_time


class PyannoteDiarizer(Diarizer):
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    @classmethod
    def from_config(cls, config: Config) -> "PyannoteDiarizer":
        token = config.HUGGING_FACE_TOKEN
        pipeline = create_pipeline("pyannote/speaker-diarization-3.1", token)
        return cls(pipeline)

    def diarize(self, audio_file: Path) -> Any:
        raw = self.pipeline(audio_file, num_speakers=2)
        return self._merge_segments(raw)

    @log_time
    def _merge_segments(self, diarization: Any) -> DiarizationResult:
        """Объединяет идущие подряд сегменты, принадлежащие одному спикеру"""

        merged: List[DiarizationSegment] = []
        current_speaker: str | None = None
        current_start: float | None = None
        current_end: float | None = None

        def append_segment():
            assert (
                current_start is not None
                and current_end is not None
                and current_speaker is not None
            )
            merged.append(
                DiarizationSegment(
                    start=timedelta(seconds=current_start),
                    end=timedelta(seconds=current_end),
                    speaker=current_speaker,
                )
            )

        for segment, _, speaker in diarization.itertracks(yield_label=True):
            if not current_speaker:
                current_speaker = speaker
                current_start = segment.start
                current_end = segment.end
                continue

            if speaker != current_speaker:
                append_segment()
                current_speaker = speaker
                current_start = segment.start
                current_end = segment.end
                continue

            current_end = segment.end

        append_segment()
        return SegmentCollection(merged)
