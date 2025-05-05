import logging
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class Diarizer(Protocol):
    def diarize(self, audio_file: Path) -> Any:
        ...
