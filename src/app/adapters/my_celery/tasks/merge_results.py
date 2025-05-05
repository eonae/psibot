from pathlib import Path

from src.app.adapters.files import storage
from src.app.core.services import MergingService


def merge_results_task(
    diarization_filename: str,
    transcription_filename: str,
    target_filename: str,
) -> None:
    merging_service = MergingService(storage)
    merging_service.merge(
        Path(transcription_filename),
        Path(diarization_filename),
        Path(target_filename),
    )
