/* eslint-disable no-console */

import type { TranscriptionJob } from '../models';
import type { FileStorage } from '../ports';

import { noop } from '@rsdk/common';
import type { SpeechToText } from '@speechkit/core';

export class TranscriptionService {
  constructor(
    private storage: FileStorage,
    private sttProviders: SpeechToText[],
  ) {}

  async transcribe(job: TranscriptionJob): Promise<void> {
    console.log(
      `🎤 Transcribing audio with ${this.sttProviders.length} providers for job ${job.id}`,
    );

    // Read WAV file from storage
    const wavData = await this.storage.read(job.paths.wav);

    // Create temporary file for STT
    const tempDir = await import('node:os');
    const tempPath = `${tempDir.tmpdir()}/speechkit-${job.id}.wav`;

    const fs = await import('node:fs/promises');
    try {
      await fs.writeFile(tempPath, new Uint8Array(wavData));

      // Run all STT providers in parallel
      const results = await Promise.allSettled(
        this.sttProviders.map((provider) => provider.transcribe(tempPath)),
      );

      // Save results from each provider
      for (const [i, result] of results.entries()) {
        const filePath =
          i === 0 ? job.paths.transcription1 : job.paths.transcription2;

        if (result.status === 'fulfilled') {
          const transcription = result.value;
          await this.storage.save(
            Buffer.from(transcription.toString()),
            filePath,
          );
          console.log(`✅ Transcription ${i + 1} completed: ${filePath}`);
        } else {
          console.error(`❌ Transcription ${i + 1} failed:`, result.reason);
          // Save error message
          await this.storage.save(
            Buffer.from(`Error: ${result.reason}`),
            filePath,
          );
        }
      }

      job.toPostprocessing();

      console.log(`✅ Transcription completed for job ${job.id}`);
    } finally {
      await fs.unlink(tempPath).catch(noop);
    }
  }
}
