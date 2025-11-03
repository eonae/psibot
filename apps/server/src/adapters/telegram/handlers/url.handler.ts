import { SourceType } from '../../../core/models';
import {
  type PipelineInput,
  pipelineWorkflow,
} from '../../../workflows/pipeline.workflow.js';

import type { Client } from '@temporalio/client';
import type { Context } from 'grammy';

export async function handleUrl(
  ctx: Context,
  temporalClient: Client,
): Promise<void> {
  const text = ctx.message?.text;
  if (!text) {
    await ctx.reply('❌ Не удалось получить текст сообщения.');
    return;
  }

  try {
    const url = new URL(text);
    if (!url.protocol || !url.hostname) {
      throw new Error('Invalid URL');
    }
  } catch {
    await ctx.reply(`❌ Неправильный URL: ${text}`);
    return;
  }

  const userId = ctx.from?.id;
  if (!userId) {
    await ctx.reply('❌ Не удалось определить пользователя.');
    return;
  }

  // Check if it's a supported URL
  if (!text.includes('drive.google.com') && !text.includes('disk.yandex.ru')) {
    await ctx.reply(
      '❌ Поддерживаются только ссылки на Яндекс.Диск и Google Drive.',
    );
    return;
  }

  const input: PipelineInput = {
    userId,
    source: {
      type: SourceType.UPLOAD_URL,
      value: text,
    },
    originalFilename: null,
  };

  await temporalClient.workflow.start(pipelineWorkflow, {
    taskQueue: 'speechkit-queue',
    workflowId: `job:${userId}:${Date.now()}`,
    args: [input],
  });

  await ctx.reply('⏳ Файл загружается...');
}
