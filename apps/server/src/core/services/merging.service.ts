/* eslint-disable no-console */

import { TranscriptionResult } from '../models';
import type { FileStorage } from '../ports';

export class MergingService {
  constructor(private storage: FileStorage) {}

  async merge(
    transcription1Path: string,
    transcription2Path: string,
    outputPath: string,
  ): Promise<void> {
    console.log(
      `🔀 Merging transcriptions: ${transcription1Path} and ${transcription2Path}`,
    );

    // Load both transcriptions
    const data1 = await this.storage.read(transcription1Path);
    const data2 = await this.storage.read(transcription2Path);

    const result1 = TranscriptionResult.parse(data1.toString());
    const result2 = TranscriptionResult.parse(data2.toString());

    // Merge results (prefer result1, fallback to result2 if segments missing)
    const merged = this.mergeTranscriptions(result1, result2);

    // Save merged result
    await this.storage.save(Buffer.from(merged.toString()), outputPath);

    console.log(`✅ Merging completed: ${outputPath}`);
  }

  private mergeTranscriptions(
    result1: TranscriptionResult,
    result2: TranscriptionResult,
  ): TranscriptionResult {
    // Simple merge strategy: prefer result1, add missing segments from result2
    const segments1 = result1.segments;
    const segments2 = result2.segments;

    const merged = [...segments1];

    // Add segments from result2 that don't overlap with result1
    for (const seg2 of segments2) {
      const overlaps = segments1.some(
        (seg1) => !(seg1.end < seg2.start || seg1.start > seg2.end),
      );

      if (!overlaps) {
        merged.push(seg2);
      }
    }

    // Sort by start time
    merged.sort((a, b) => a.start - b.start);

    return new TranscriptionResult(merged);
  }
}
