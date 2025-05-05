"""Модуль с базовым классом сегмента"""

import re
from datetime import timedelta
from typing import Optional, Self

from src.shared.time import format_timedelta, parse_timedelta


class Segment:
    """Базовый класс для всех типов сегментов"""

    start: timedelta
    end: timedelta
    speaker: Optional[str] = None
    text: Optional[str] = None

    def __init__(
        self,
        start: timedelta,
        end: timedelta,
        speaker: Optional[str] = None,
        text: Optional[str] = None,
    ):
        self.start = start
        self.end = end
        self.speaker = speaker
        self.text = text

    def __str__(self) -> str:
        start = format_timedelta(self.start)
        end = format_timedelta(self.end)
        parts = [f"[{start} - {end}]"]

        if self.speaker:
            parts.append(f"[{self.speaker}]")

        if self.text:
            parts.append(self.text)

        return " ".join(parts)

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_segment(cls, segment: "Segment") -> Self:
        """Создает новый сегмент из базового сегмента.

        Args:
            segment: Базовый сегмент для создания нового

        Returns:
            Новый сегмент того же типа
        """
        return cls(
            start=segment.start,
            end=segment.end,
            speaker=segment.speaker,
            text=segment.text,
        )

    @classmethod
    def parse(cls, text: str) -> Self:
        """Парсит строку в формате [START - END] [SPEAKER] TEXT"""
        pattern = r"\[(.*?) - (.*?)\](?: \[(.*?)\])?(?: (.*))?"
        match = re.match(pattern, text)
        if not match:
            raise ValueError(f"Неверный формат строки: {text}")

        start_str = match.group(1)
        end_str = match.group(2)
        speaker = match.group(3)
        text = match.group(4)

        start = parse_timedelta(start_str)
        end = parse_timedelta(end_str)

        return cls(start=start, end=end, speaker=speaker, text=text)
