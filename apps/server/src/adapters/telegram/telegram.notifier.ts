import type { Notifier } from '../../core/ports';

import type { Bot } from 'grammy';
import { InputFile } from 'grammy';

export class TelegramNotifier implements Notifier {
  constructor(private bot: Bot) {}

  async notify(userId: number, message: string): Promise<void> {
    await this.bot.api.sendMessage(userId, message);
  }

  async sendDocument(
    userId: number,
    file: Buffer,
    filename: string,
    caption: string,
  ): Promise<void> {
    const inputFile = new InputFile(new Uint8Array(file), filename);
    await this.bot.api.sendDocument(userId, inputFile, {
      caption,
    });
  }

  async sendProgress(userId: number, message: string): Promise<void> {
    await this.notify(userId, message);
  }
}
