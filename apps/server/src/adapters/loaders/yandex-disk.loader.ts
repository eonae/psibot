import type { FileSource } from '../../core/models';
import { SourceType } from '../../core/models';

import { BaseLoader } from './base';

import axios from 'axios';

export class YandexDiskFileLoader extends BaseLoader {
  supports(source: FileSource): boolean {
    if (source.type !== SourceType.UPLOAD_URL) {
      return false;
    }

    try {
      const url = new URL(source.value);
      return url.hostname.includes('disk.yandex.ru');
    } catch {
      return false;
    }
  }

  async getDownloadUrl(source: FileSource): Promise<string> {
    const url = source.value;

    // Extract file ID from URL
    const match = url.match(/\/d\/([^/]+)/);
    if (!match) {
      throw new Error('Could not extract file ID from Yandex Disk URL');
    }

    // Get download link from Yandex API
    const apiUrl = `https://cloud-api.yandex.net/v1/disk/public/resources?public_key=${encodeURIComponent(url)}`;

    try {
      const response = await axios.get(apiUrl, { timeout: 20_000 });

      if (!response.data.file) {
        throw new Error('No download link in Yandex Disk response');
      }

      return response.data.file;
    } catch (error) {
      throw new Error(`Failed to get download URL from Yandex Disk: ${error}`);
    }
  }
}
