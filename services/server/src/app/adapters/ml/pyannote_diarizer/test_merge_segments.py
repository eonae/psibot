"""
Тесты для функции merge_segments.
"""

from pathlib import Path

import pytest  # type: ignore
from pyannote.audio import Pipeline  # type: ignore
from pyannote.core import Segment  # type: ignore
from src.app.core.models import DiarizationSegment, SegmentCollection

from .pyannote_diarizer import PyannoteDiarizer


class DummyPipeline(Pipeline):  # pylint: disable=abstract-method
    """
    Мок-класс для Pipeline.
    """

    def __call__(self, audio_file, num_speakers=2):
        """
        Мок-метод для Pipeline.
        """

        class MockDiarization:
            """
            Мок-класс для Diarization.
            """

            def itertracks(self, yield_label=True):
                # pylint: disable=unused-argument

                """
                Мок-метод для itertracks.
                """

                # SPEAKER_01
                yield Segment(0.030, 31.418), None, "SPEAKER_01"
                # SPEAKER_00
                yield Segment(34.506, 60.983), None, "SPEAKER_00"

        return MockDiarization()


def test_pyannote_diarizer_returns_segment_collection():
    """
    Тест для функции diarize.
    """

    diarizer = PyannoteDiarizer(DummyPipeline())
    result = diarizer.diarize(Path("dummy.wav"))

    assert isinstance(result, SegmentCollection)
    assert len(result) == 2

    segment1, segment2 = result
    assert isinstance(segment1, DiarizationSegment)
    assert isinstance(segment2, DiarizationSegment)
    assert segment1.start.total_seconds() == pytest.approx(0.030)
    assert segment1.end.total_seconds() == pytest.approx(31.418)
    assert segment1.speaker == "SPEAKER_01"
    assert segment2.speaker == "SPEAKER_00"
