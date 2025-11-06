import type { JobInitInput, JobStateDTO } from '../activities/index.js';

import {
  defineQuery,
  defineSignal,
  proxyActivities,
  setHandler,
} from '@temporalio/workflow';

const activities = proxyActivities<{
  createJob(input: JobInitInput): Promise<JobStateDTO>;
  notify(userId: number, message: string): Promise<void>;
  download(job: JobStateDTO): Promise<JobStateDTO>;
  convert(job: JobStateDTO): Promise<JobStateDTO>;
  transcribe(job: JobStateDTO): Promise<JobStateDTO>;
  postprocess(job: JobStateDTO): Promise<JobStateDTO>;
  sendResult(job: JobStateDTO): Promise<void>;
}>({
  startToCloseTimeout: '1 hour',
  retry: { initialInterval: '5s', backoffCoefficient: 2, maximumAttempts: 3 },
});

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface PipelineInput extends JobInitInput {}

export const statusQuery = defineQuery<string>('status');
export const cancelSignal = defineSignal('cancel');

export async function pipelineWorkflow(input: PipelineInput): Promise<void> {
  let status = 'pending';
  let cancelled = false;

  setHandler(statusQuery, () => status);
  setHandler(cancelSignal, () => {
    cancelled = true;
  });

  let job = await activities.createJob(input);

  if (cancelled) {
    return;
  }
  status = 'downloading';
  await activities.notify(job.userId, '⏳ Файл загружается...');
  job = await activities.download(job);

  if (cancelled) {
    return;
  }
  status = 'converting';
  await activities.notify(job.userId, '🔄 Аудио конвертируется в WAV...');
  job = await activities.convert(job);

  if (cancelled) {
    return;
  }
  status = 'transcribing';
  await activities.notify(job.userId, '🎤 Выполняется распознавание речи...');
  job = await activities.transcribe(job);

  if (cancelled) {
    return;
  }
  if (cancelled) {
    return;
  }
  status = 'postprocessing';
  await activities.notify(job.userId, '✨ Выполняется постобработка...');
  job = await activities.postprocess(job);

  if (cancelled) {
    return;
  }
  status = 'sending';
  await activities.sendResult(job);

  status = 'completed';
}
