/* eslint-disable unicorn/no-process-exit */
/* eslint-disable no-console */

import 'dotenv/config';

import { setupBotHandlers } from './adapters/telegram/bot';
import { Config } from './config';

import { Client, Connection } from '@temporalio/client';

async function main(): Promise<void> {
  console.log('🚀 Starting SpeechKit server...');

  const config = new Config();

  // Create bot
  const { Bot } = await import('grammy');
  const bot = new Bot(config.TELEGRAM_BOT_TOKEN);

  // Temporal Client
  const connection = await Connection.connect({
    address: config.TEMPORAL_ADDRESS,
  });
  const temporalClient = new Client({ connection });
  console.log('✅ Temporal client connected');

  // Setup bot handlers
  setupBotHandlers(bot, temporalClient);
  console.log('✅ Telegram bot configured');

  // Start bot
  await bot.start();
  console.log('✅ Telegram bot started');

  console.log('🎉 SpeechKit server is ready!');
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
