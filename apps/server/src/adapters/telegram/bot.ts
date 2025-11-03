import { handleFile, handleUrl, registerCommands } from './handlers';

import type { Client } from '@temporalio/client';
import type { Bot } from 'grammy';

export function setupBotHandlers(bot: Bot, temporalClient: Client): void {
  registerCommands(bot);

  bot.on('message:audio', (ctx) => handleFile(ctx, temporalClient));
  bot.on('message:document', (ctx) => handleFile(ctx, temporalClient));
  bot.on('message:voice', (ctx) => handleFile(ctx, temporalClient));

  // Handle URLs
  bot.on('message:text', (ctx) => handleUrl(ctx, temporalClient));
}
