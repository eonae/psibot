import type { TranscriptionResult } from './transcription-result.class';

export interface SpeechToText {
  transcribe(audioPath: string): Promise<TranscriptionResult>;
}
