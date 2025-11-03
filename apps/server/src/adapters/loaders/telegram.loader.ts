import type { FileSource } from '../../core/models';
import { SourceType } from '../../core/models';

import { BaseLoader } from './base';

import axios from 'axios';

const TELEGRAM_BASE_URL = 'https://api.telegram.org';

export class TelegramFileLoader extends BaseLoader {
  private botToken: string;

  constructor(botToken: string) {
    super();
    this.botToken = botToken;
  }

  supports(source: FileSource): boolean {
    return source.type === SourceType.TELEGRAM_FILE_ID;
  }

  async getDownloadUrl(source: FileSource): Promise<string> {
    const fileId = source.value;

    // Validate file_id
    if (!/^[\w-]+$/.test(fileId)) {
      throw new Error('Invalid Telegram file_id');
    }

    // Get file info
    const url = `${TELEGRAM_BASE_URL}/bot${this.botToken}/getFile`;
    const response = await axios.get(url, {
      params: { file_id: fileId },
      timeout: 10_000,
    });

    const filePath = response.data.result?.file_path;
    if (!filePath) {
      throw new Error('Failed to get file path from Telegram');
    }

    return `${TELEGRAM_BASE_URL}/file/bot${this.botToken}/${filePath}`;
  }
}
