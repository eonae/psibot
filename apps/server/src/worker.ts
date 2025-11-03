/* eslint-disable unicorn/no-process-exit */
/* eslint-disable no-console */

import { join } from 'node:path';

import 'dotenv/config';

import { OpenRouterAdapter } from './adapters/llm';
import {
  GoogleDriveFileLoader,
  TelegramFileLoader,
  YandexDiskFileLoader,
} from './adapters/loaders';
import { LocalFileStorage, S3Bucket } from './adapters/storage';
import { TelegramNotifier } from './adapters/telegram/telegram.notifier';
import { MergingService, PostprocessingService } from './core/services';
import { buildActivities } from './activities';
import { Config } from './config';

import { SaluteSpeechAdapter } from '@speechkit/salute';
import { YandexSpeechKitAdapter } from '@speechkit/yandex';
import { Worker } from '@temporalio/worker';
import dotenv from 'dotenv';
import { Bot } from 'grammy';

dotenv.config();

async function run(): Promise<void> {
  console.log('🛠️ Starting Temporal worker...');

  const config = new Config();

  const storage = new LocalFileStorage(config.STORAGE_PATH);

  const s3Bucket = new S3Bucket(
    config.YC_S3_ENDPOINT,
    config.YC_ACCESS_KEY_ID,
    config.YC_SECRET_ACCESS_KEY,
    config.YC_SPEECH_KIT_BUCKET_NAME,
  );

  const loaders = [
    new TelegramFileLoader(config.TELEGRAM_BOT_TOKEN),
    new YandexDiskFileLoader(),
    new GoogleDriveFileLoader(),
  ];

  const sttProviders = [
    new YandexSpeechKitAdapter(config.YC_API_KEY, s3Bucket),
    new SaluteSpeechAdapter(
      config.SALUTE_SPEECH_AUTH_KEY,
      config.SALUTE_SPEECH_SCOPE,
    ),
  ];

  const llm = new OpenRouterAdapter(config.OPENROUTER_API_KEY);
  const mergingService = new MergingService(storage);
  const postprocessor = new PostprocessingService(storage, llm);

  const bot = new Bot(config.TELEGRAM_BOT_TOKEN);
  const notifier = new TelegramNotifier(bot);

  const activities = buildActivities({
    loaders,
    storage,
    sttProviders,
    mergingService,
    postprocessor,
    notifier,
  });

  const worker = await Worker.create({
    workflowsPath: join(__dirname, 'workflows', 'pipeline.workflow.ts'),
    activities,
    taskQueue: 'speechkit-queue',
  });

  await worker.run();
}

run().catch((error) => {
  console.error('❌ Temporal worker failed:', error);
  process.exit(1);
});
