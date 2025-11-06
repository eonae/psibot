/* eslint-disable no-console */

import type { TranscriptionJob } from '../models';
import type { FileStorage, LLM } from '../ports';

const PROMPT_TEMPLATE = `
Ты — профессиональный психолог. На вход тебе даётся результат распознавания
аудиозаписи психоаналитической сессии.

Твои задачи:

1. Объединяй подряд идущие строки, если они явно являются частью одного предложения.
   При объединении сохраняй таймкоды первой строки объединения.
   Следи за тем, чтобы объединённые реплики были не слишком длинными.

2. Отредактируй текст внутри каждой строки:
   - Разбей чрезмерно длинные фразы на предложения;
   - Поставь корректные знаки препинания;
   - Исправь очевидные ошибки распознавания (например, "стыкой" → "стыковка").

3. Сохраняй исходный формат входных данных. НЕ добавляй информацию о спикерах (SPEAKER_00, SPEAKER_01 и т.п.), если её не было во входных данных.

ВАЖНО: Возвращай ТОЛЬКО результат обработки в том же формате, что и входные данные, без каких-либо дополнительных комментариев, описаний, заголовков, разметки или пояснений. Никаких предисловий типа "Конечно, давайте...", "Отредактированный текст:" и т.п.

Пример входа:

[0:00.000 - 0:04.319] мужчина даже не мог их видеть стыкой это пропаганда
[0:04.319 - 0:09.800] ислама сири что делать

Пример результата:

[0:00.000 - 0:04.319] Мужчина даже не мог их видеть. Стыковка — это пропаганда ислама.
[0:04.319 - 0:09.800] Сири, что делать?

- - - - - - - - - - - - -

Задача

- - - - - - - - - - - - -

{text}
`;

export class PostprocessingService {
  constructor(
    private storage: FileStorage,
    private llm: LLM,
  ) {}

  async postprocess(job: TranscriptionJob): Promise<void> {
    console.log(`✨ Postprocessing transcript for job ${job.id}`);

    // Load Yandex transcript
    const yandexData = await this.storage.read(job.paths.transcription1);
    const yandexText = yandexData.toString();

    // Process with LLM
    const prompt = PROMPT_TEMPLATE.replace('{text}', yandexText);

    // Ensure postprocessingPrompt path exists (for backward compatibility with old jobs)
    const promptPath =
      job.paths.postprocessingPrompt ||
      job.paths.postprocessed.replace(
        'postprocessed.txt',
        'postprocessing_prompt.txt',
      );

    // Save prompt to file
    try {
      await this.storage.save(Buffer.from(prompt), promptPath);
      console.log(`📝 Postprocessing prompt saved: ${promptPath}`);
    } catch (error) {
      console.error(
        `❌ Failed to save postprocessing prompt to ${promptPath}:`,
        error,
      );
      throw error;
    }

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
