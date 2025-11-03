import crypto from 'node:crypto';

import type { FileSource } from './file-source.js';
import { JobStatus } from './job-status.js';

export interface TranscriptionJobPaths {
  original: string;
  wav: string;
  transcription1: string; // Yandex SpeechKit
  transcription2: string; // Salute
  merged: string;
  postprocessed: string;
}

export class TranscriptionJob {
  id: string;
  userId: number;
  source: FileSource;
  originalFilename: string | null;
  status: JobStatus;
  createdAt: Date;
  updatedAt: Date;
  paths: TranscriptionJobPaths;
  error?: string;

  constructor(
    userId: number,
    source: FileSource,
    originalFilename: string | null = null,
  ) {
    this.id = crypto.randomUUID();
    this.userId = userId;
    this.source = source;
    this.originalFilename = originalFilename;
    this.status = JobStatus.DOWNLOADING;
    this.createdAt = new Date();
    this.updatedAt = new Date();

    const timestamp = Math.floor(this.createdAt.getTime() / 1000);
    const basePath = `${timestamp}_${this.id}`;

    this.paths = {
      original: `${basePath}/original_${originalFilename || 'file'}`,
      wav: `${basePath}/converted.wav`,
      transcription1: `${basePath}/transcription_yandex.txt`,
      transcription2: `${basePath}/transcription_salute.txt`,
      merged: `${basePath}/merged.txt`,
      postprocessed: `${basePath}/postprocessed.txt`,
    };
  }

  isActive(): boolean {
    return ![
      JobStatus.FAILED,
      JobStatus.CONFIRMED,
      JobStatus.REJECTED,
    ].includes(this.status);
  }

  toConverting(): void {
    this.transition(JobStatus.DOWNLOADING, JobStatus.CONVERTING);
  }

  toTranscribing(): void {
    this.transition(JobStatus.CONVERTING, JobStatus.TRANSCRIBING);
  }

  toPostprocessing(): void {
    this.transition(JobStatus.TRANSCRIBING, JobStatus.POSTPROCESSING);
  }

  toConfirmation(): void {
    this.transition(JobStatus.POSTPROCESSING, JobStatus.PENDING_CONFIRMATION);
  }

  setConfirmed(): void {
    this.transition(JobStatus.PENDING_CONFIRMATION, JobStatus.CONFIRMED);
  }

  setRejected(): void {
    this.transition(JobStatus.PENDING_CONFIRMATION, JobStatus.REJECTED);
  }

  setFailed(error: Error): void {
    if (!this.isActive()) {
      throw new Error(`Job ${this.id} is not in active status`);
    }
    this.status = JobStatus.FAILED;
    this.error = error.message;
    this.updatedAt = new Date();
  }

  private transition(from: JobStatus, to: JobStatus): void {
    if (this.status !== from) {
      throw new Error(
        `Job ${this.id} can't transition to ${to}, expected ${from}, got ${this.status}`,
      );
    }
    this.status = to;
    this.updatedAt = new Date();
  }
}
