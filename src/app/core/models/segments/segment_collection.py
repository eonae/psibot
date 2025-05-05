"""Основной модуль приложения"""

from typing import Iterator, List, Type

from .segment_base import Segment


class SegmentCollection[S: Segment]:
    """Коллекция сегментов"""

    def __init__(self, segments: List[S] | None = None):
        self._segments = segments or []

    def append(self, segment: S) -> None:
        """Добавляет сегмент в коллекцию"""
        self._segments.append(segment)

    def extend(self, segments: "SegmentCollection[S]") -> None:
        """Добавляет сегменты в коллекцию"""
        self._segments.extend(segments)

    def __iter__(self) -> Iterator[S]:
        return iter(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def __getitem__(self, index: int) -> S:
        return self._segments[index]

    def __str__(self) -> str:
        return "\n".join(str(segment) for segment in self._segments)

    def __repr__(self) -> str:
        return f"SegmentCollection({self._segments})"

    @staticmethod
    def parse[T: Segment](text: str, segment_class: Type[T]) -> "SegmentCollection[T]":
        """Парсит текст в коллекцию сегментов.

        Args:
            text: Текст для парсинга
            segment_class: Класс сегмента, который должен иметь метод from_segment
        """
        return SegmentCollection(
            [
                segment_class.from_segment(Segment.parse(line))
                for line in text.split("\n")
                if line
            ]
        )

    def split(self, max_chars: int) -> List["SegmentCollection[S]"]:
        """Разбивает коллекцию на чанки с ограничением по количеству символов."""
        chunks: List[SegmentCollection[S]] = []
        current_chunk = SegmentCollection[S]()
        current_chars = 0

        for segment in self:
            segment_str = str(segment).replace("\n", "\\n")
            if current_chars + len(segment_str) > max_chars and len(current_chunk) > 0:
                chunks.append(current_chunk)
                current_chunk = SegmentCollection[S]()
                current_chars = 0
            current_chunk.append(segment)
            current_chars += len(segment_str)
        if len(current_chunk) > 0:
            chunks.append(current_chunk)
        return chunks
