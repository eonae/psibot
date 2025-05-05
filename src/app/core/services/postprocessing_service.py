import logging
import re
from pathlib import Path
from typing import List

from src.app.core.models import (
    MergedTranscriptionResult,
    TranscriptionSegmentWithSpeaker,
    SegmentCollection,
)
from src.app.core.ports import FileStorage
from src.app.core.ports.ml import Gpt
from src.shared.logging import log_time

logger = logging.getLogger(__name__)

# pylint: disable=line-too-long
# flake8: noqa: E501
PROMPT_TEMPLATE = """
    Ты — профессиональный редактор. На вход тебе даётся результат распознавания
    аудиозаписи психоаналитической сессии. Один из говорящих — терапевт, другой — клиент.

    Твои задачи:

    1. Определи роли спикеров (терапевт / клиент) на основе речевых признаков (см. ниже).

    2. Объединяй подряд идущие реплики, если они:
    - принадлежат одному и тому же говорящему;
    - очень короткие;
    - явно являются частью одного предложения;

    3. При объединении бери номер строки первой строки объединения

    4. Отредактируй текст внутри объединённой реплики:
    - Разбей чрезмерно длинные фразы на предложения, даже если там везде "и";
    - Поставь корректные знаки препинания;
    - Начни предложения с заглавной буквы;
    - Не перефразируй, кроме случаев явной ошибки распознавания.

    5. Формат каждого объединённого высказывания:
    N [SPEAKER в формате "Т"/"К"] текст без переводов строк

    Признаки ролей:

    Терапевт:
    - Использует формулировки вроде: "я думаю", "похоже", "вам тяжело", "вы чувствуете"
    - Часто интерпретирует, поддерживает, отражает эмоции
    - В основном комментирует слова клиента

    Клиент:
    - Говорит о себе: "я чувствую", "мне кажется", "я сказал", "я заметила"
    - Делится личными переживаниями, описывает действия, воспоминания

    Пример входа:

    0 [SPEAKER_01] мне кажется я слишком остро реагирую на критику
    1 [SPEAKER_01] потом весь день хожу и прокручиваю это в голове
    2 [SPEAKER_00] звучит так будто это не просто про критику а про то как вы её воспринимаете
    3 [SPEAKER_00] как будто она вас задевает глубже чем просто замечание

    Результат:

    0 [К] Мне кажется, я слишком остро реагирую на критику. Потом весь день хожу и прокручиваю это в голове.
    2 [Т] Звучит так, будто это не просто про критику, а про то, как вы её воспринимаете. Как будто она задевает вас глубже, чем просто замечание.

    {text}
"""


class PostprocessingService:
    def __init__(self, storage: FileStorage, gpt: Gpt):
        self.storage = storage
        self.gpt = gpt

    def postprocess(self, source_filename: Path, target_filename: Path) -> None:
        """Пост-обработка результатов распознавания

        Args:
            source_filename: Путь к файлу с объединенными результатами
            target_filename: Путь для сохранения результата
        """
        logger.info("🎯 Starting post-processing of %s...", source_filename)

        text_data = self.storage.read(Path(source_filename)).decode()
        parsed_data = SegmentCollection.parse(text_data, TranscriptionSegmentWithSpeaker)

        transformed_results = self._transform(parsed_data)

        self.storage.save(str(transformed_results).encode(), Path(target_filename))

        logger.info("✅ Post-processing completed: %s", target_filename)

    @log_time
    def _transform(self, results: MergedTranscriptionResult) -> MergedTranscriptionResult:
        """Пост-обработка результатов распознавания

        Args:
            results: Результаты распознавания
        """

        transformed_chunks: List[MergedTranscriptionResult] = []

        chunks = results.split(self.gpt.MAX_SYMBOLS)

        for i, chunk in enumerate(chunks):
            logger.info("Processing chunk %d of %d", i + 1, len(chunks))
            # Заменяем переносы строк на специальный маркер
            text = "\n".join([f"{i} {str(line)}" for i, line in enumerate(chunk)])
            prompt = PROMPT_TEMPLATE.format(text=text)
            logger.debug("Prompt for chunk %d:\n %s", i + 1, prompt)

            response = self.gpt.reply(prompt)
            logger.debug("GPT Response for chunk %d:\n %s", i + 1, response)

            # Восстанавливаем переносы строк в ответе
            transformed_chunk: SegmentCollection[TranscriptionSegmentWithSpeaker] = (
                SegmentCollection()
            )

            lines = [line for line in response.split("\n") if line]

            for i, line in enumerate(lines):
                # Парсим номер строки, спикера и текст
                pattern = r"(\d+)\s+\[(.*?)\]\s+(.*)"
                match = re.match(pattern, line)
                if not match:
                    continue

                line_number = int(match.group(1))
                speaker = match.group(2)
                text = match.group(3)

                # Находим соответствующий сегмент в исходных данных
                if line_number >= len(chunk):
                    logger.warning(
                        "Line number %d is out of range (chunk size: %d)",
                        line_number,
                        len(chunk),
                    )
                    continue

                original_segment = chunk[line_number]

                # Определяем end время
                if i < len(lines) - 1:
                    next_line = lines[i + 1]
                    next_match = re.match(pattern, next_line)
                    if next_match:
                        next_line_number = int(next_match.group(1))
                        if next_line_number >= len(chunk):
                            end_time = original_segment.end
                        else:
                            end_segment = chunk[next_line_number]
                            end_time = end_segment.start
                    else:
                        end_time = original_segment.end
                else:
                    end_time = original_segment.end

                # Создаем новый сегмент с правильными временами
                new_segment = TranscriptionSegmentWithSpeaker(
                    start=original_segment.start,
                    end=end_time,
                    speaker=speaker,
                    text=text,
                )

                transformed_chunk.append(new_segment)

            transformed_chunks.append(transformed_chunk)

        return SegmentCollection(
            [segment for chunk in transformed_chunks for segment in chunk]
        )
