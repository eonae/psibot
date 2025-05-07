import logging
from pathlib import Path
from typing import Type
from src.app.core.models import (
    DiarizationSegment,
    TranscriptionSegment,
    SegmentCollection,
    DiarizationResult,
    TranscriptionResult,
    MergedTranscriptionResult,
)
from src.app.core.models.segments.segment_base import Segment
from src.app.core.ports.file_storage import FileStorage
from src.shared.logging import log_time


logger = logging.getLogger(__name__)


class MergingService:
    def __init__(self, storage: FileStorage):
        self.storage = storage

    @log_time
    def merge(
        self,
        transcription_filename: Path,
        diarization_filename: Path,
        target_filename: Path,
    ) -> None:
        """Объединение результатов диаризации и распознавания

        Args:
            transcription_filename: Путь к файлу с результатом распознавания
            diarization_filename: Путь к файлу с диаризацией
            target_filename: Путь для сохранения результата
        """

        logger.info("🎯 Starting merging results for %s...", target_filename)

        transcription = self._load(transcription_filename, TranscriptionSegment)
        diarization = self._load(diarization_filename, DiarizationSegment)

        print(f"transcription: {transcription}")
        print(f"diarization: {diarization}")
        merged = self._merge(transcription=transcription, diarization=diarization)
        self.storage.save(str(merged).encode(), target_filename)

        logger.info("✅ Merging completed: %s", target_filename)

    def _merge(
        self,
        transcription: TranscriptionResult,
        diarization: DiarizationResult,
    ) -> MergedTranscriptionResult:
        merged: MergedTranscriptionResult = SegmentCollection()

        for t_segment in transcription:
            to_append = None
            for d_segment in diarization:
                if t_segment.start > d_segment.end or t_segment.end < d_segment.start:
                    continue

                to_append = t_segment.with_speaker(d_segment.speaker)
                break

            if to_append:
                merged.append(to_append)
            else:
                raise ValueError(
                    f"Не удалось найти подходящий сегмент диаризации для {t_segment}"
                )

        return merged

    def _load[S: Segment](
        self, filename: Path, segment_type: Type[S]
    ) -> SegmentCollection[S]:
        data = self.storage.read(filename)
        return SegmentCollection.parse(data.decode(), segment_type)
