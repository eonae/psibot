import type { FileSource, JobStatus } from '../core/models';
import { TranscriptionJob } from '../core/models';
import type { FileLoader, FileStorage, Notifier } from '../core/ports';
import type { MergingService, PostprocessingService } from '../core/services';
import {
  ConversionService,
  DownloadService,
  TranscriptionService,
} from '../core/services';

import type { SpeechToText } from '@speechkit/core';

export interface ActivityDeps {
  loaders: FileLoader[];
  storage: FileStorage;
  sttProviders: SpeechToText[];
  mergingService: MergingService;
  postprocessor: PostprocessingService;
  notifier: Notifier;
}

export interface JobInitInput {
  userId: number;
  source: FileSource;
  originalFilename: string | null;
}

export interface JobStateDTO {
  id: string;
  userId: number;
  source: FileSource;
  originalFilename: string | null;
  paths: TranscriptionJob['paths'];
  status: JobStatus;
  createdAt: string; // ISO string
  updatedAt: string; // ISO string
  error?: string;
}

function jobFromDTO(dto: JobStateDTO): TranscriptionJob {
  // Восстанавливаем объект задания для сервисов
  const job = new TranscriptionJob(
    dto.userId,
    dto.source,
    dto.originalFilename,
  );
  job.id = dto.id;
  job.paths = dto.paths;
  job.status = dto.status;
  job.createdAt = new Date(dto.createdAt);
  job.updatedAt = new Date(dto.updatedAt);
  if (dto.error) {
    job.error = dto.error;
  }
  return job;
}

function jobToDTO(job: TranscriptionJob): JobStateDTO {
  return {
    id: job.id,
    userId: job.userId,
    source: job.source,
    originalFilename: job.originalFilename,
    paths: job.paths,
    status: job.status,
    createdAt: job.createdAt.toISOString(),
    updatedAt: job.updatedAt.toISOString(),
    error: job.error,
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function buildActivities(deps: ActivityDeps) {
  const downloadService = new DownloadService(deps.loaders, deps.storage);
  const conversionService = new ConversionService(deps.storage);
  const transcriptionService = new TranscriptionService(
    deps.storage,
    deps.sttProviders,
  );

  return {
    async createJob(input: JobInitInput): Promise<JobStateDTO> {
      const job = new TranscriptionJob(
        input.userId,
        input.source,
        input.originalFilename,
      );
      return jobToDTO(job);
    },

    async notify(userId: number, message: string): Promise<void> {
      await deps.notifier.sendProgress(userId, message);
    },

    async download(jobDto: JobStateDTO): Promise<JobStateDTO> {
      const job = jobFromDTO(jobDto);
      await downloadService.download(job);
      return jobToDTO(job);
    },

    async convert(jobDto: JobStateDTO): Promise<JobStateDTO> {
      const job = jobFromDTO(jobDto);
      await conversionService.convert(job);
      return jobToDTO(job);
    },

    async transcribe(jobDto: JobStateDTO): Promise<JobStateDTO> {
      const job = jobFromDTO(jobDto);
      await transcriptionService.transcribe(job);
      return jobToDTO(job);
    },

    async merge(jobDto: JobStateDTO): Promise<JobStateDTO> {
      const job = jobFromDTO(jobDto);
      await deps.mergingService.merge(
        job.paths.transcription1,
        job.paths.transcription2,
        job.paths.merged,
      );
      return jobToDTO(job);
    },

    async postprocess(jobDto: JobStateDTO): Promise<JobStateDTO> {
      const job = jobFromDTO(jobDto);
      await deps.postprocessor.postprocess(job);
      return jobToDTO(job);
    },

    async sendResult(jobDto: JobStateDTO): Promise<void> {
      // Финальная отправка результата пользователю
      const job = jobFromDTO(jobDto);
      const resultFilename = job.originalFilename
        ? job.originalFilename.replace(/\.[^./]+$/, '.txt')
        : `transcription_${job.id}.txt`;
      const data = await deps.storage.read(job.paths.postprocessed);
      await deps.notifier.sendDocument(
        job.userId,
        data,
        resultFilename,
        '✅ Обработка завершена!',
      );
    },
  };
}
