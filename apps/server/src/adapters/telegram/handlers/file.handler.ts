/* eslint-disable no-console */

import { SourceType } from '../../../core/models';
import {
  type PipelineInput,
  pipelineWorkflow,
} from '../../../workflows/pipeline.workflow.js';

import type { Client } from '@temporalio/client';
import type { Context } from 'grammy';

export async function handleFile(
  ctx: Context,
  temporalClient: Client,
): Promise<void> {
  console.log('📥 Received file message');
  const file =
    ctx.message?.audio || ctx.message?.document || ctx.message?.voice;
  if (!file) {
    console.log('❌ No file found in message');
    await ctx.reply(
      '❌ Не удалось распознать файл. Пожалуйста, отправьте аудиофайл.',
    );
    return;
  }

  // Check if audio
  if ('mime_type' in file && !file.mime_type?.startsWith('audio/')) {
    await ctx.reply(
      `❌ Это не аудиофайл (тип '${file.mime_type}'). Пожалуйста, отправьте аудиофайл одного из поддерживаемых форматов: mp3, m4a, ogg, wav, webm`,
    );
    return;
  }

  const userId = ctx.from?.id;
  if (!userId) {
    await ctx.reply('❌ Не удалось определить пользователя.');
    return;
  }

  const originalFilename = 'file_name' in file ? file.file_name : null;

  const input: PipelineInput = {
    userId,
    source: {
      type: SourceType.TELEGRAM_FILE_ID,
      value: file.file_id,
    },
    originalFilename: originalFilename ?? null,
  };

  // Start Temporal workflow
  await temporalClient.workflow.start(pipelineWorkflow, {
    taskQueue: 'speechkit-queue',
    workflowId: `job:${userId}:${Date.now()}`,
    args: [input],
  });

  await ctx.reply('⏳ Файл загружается...');
}
