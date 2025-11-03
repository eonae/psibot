import type { FileSource } from '../../core/models';
import { SourceType } from '../../core/models';

import { BaseLoader } from './base';

export class GoogleDriveFileLoader extends BaseLoader {
  supports(source: FileSource): boolean {
    if (source.type !== SourceType.UPLOAD_URL) {
      return false;
    }

    try {
      const url = new URL(source.value);
      return url.hostname.includes('drive.google.com');
    } catch {
      return false;
    }
  }

  async getDownloadUrl(source: FileSource): Promise<string> {
    const url = source.value;

    // Extract file ID from URL
    const match = url.match(/\/file\/d\/([^/]+)/);
    if (!match) {
      throw new Error('Could not extract file ID from Google Drive URL');
    }

    const fileId = match[1];

    // Construct download URL
    return `https://drive.google.com/uc?export=download&id=${fileId}`;
  }
}
