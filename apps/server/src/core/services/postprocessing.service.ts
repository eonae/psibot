/* eslint-disable no-console */

import type { TranscriptionJob } from '../models';
import type { FileStorage, LLM } from '../ports';

const PROMPT_TEMPLATE = `
Ты — профессиональный психолог. На вход тебе даётся результат распознавания
аудиозаписи психоаналитической сессии. Один из говорящих — терапевт, другой — клиент.

Твои задачи:

1. Объединяй подряд идущие реплики, если они:
- принадлежат одному и тому же говорящему;
- явно являются частью одного предложения;
- следи за тем, чтобы объединённые реплики были не слишком длинными.

2. При объединении бери номер строки первой строки объединения

3. Отредактируй текст внутри объединённой реплики:
- Разбей чрезмерно длинные фразы на предложения;
- Поставь корректные знаки препинания;

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

0 [SPEAKER_01] Мне кажется, я слишком остро реагирую на критику. Потом весь день хожу и прокручиваю это в голове.
1 [SPEAKER_00] Звучит так, будто это не просто про критику, а про то, как вы её воспринимаете. Как будто она задевает вас глубже, чем просто замечание.

{text}
`;

export class PostprocessingService {
  constructor(
    private storage: FileStorage,
    private llm: LLM,
  ) {}

  async postprocess(job: TranscriptionJob): Promise<void> {
    console.log(`✨ Postprocessing transcript for job ${job.id}`);

    // Load merged transcript
    const mergedData = await this.storage.read(job.paths.merged);
    const mergedText = mergedData.toString();

    // Process with LLM
    const prompt = PROMPT_TEMPLATE.replace('{text}', mergedText);
    const processedText = await this.llm.process(prompt);

    // Save processed result
    await this.storage.save(
      Buffer.from(processedText),
      job.paths.postprocessed,
    );

    job.toConfirmation();

    console.log(`✅ Postprocessing completed: ${job.paths.postprocessed}`);
  }
}
