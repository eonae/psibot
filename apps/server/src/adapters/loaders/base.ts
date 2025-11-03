/* eslint-disable no-console */
import type { FileSource } from '../../core/models';
import type { FileLoader } from '../../core/ports';

import type { AxiosResponse } from 'axios';
import axios from 'axios';

export abstract class BaseLoader implements FileLoader {
  abstract supports(source: FileSource): boolean;
  abstract getDownloadUrl(source: FileSource): Promise<string>;

  async load(source: FileSource): Promise<Buffer> {
    console.log('Getting download URL...');
    const downloadUrl = await this.getDownloadUrl(source);
    console.log('Download URL:', downloadUrl);

    try {
      const response: AxiosResponse<ArrayBuffer> = await axios.get<ArrayBuffer>(
        downloadUrl,
        {
          responseType: 'arraybuffer',
          timeout: 30_000,
        },
      );

      console.log(
        `✅ File downloaded successfully (${response.data.byteLength} bytes)`,
      );

      return Buffer.from(new Uint8Array(response.data));
    } catch (error) {
      console.error('❌ Error downloading file:', error);
      throw new Error(`Failed to download file: ${error}`);
    }
  }

  protected extractFilename(contentDisposition: string): string | null {
    const filenameMatch = contentDisposition.match(
      /filename[^\n;=]*=((["']).*?\2|[^\n;]*)/,
    );
    if (!filenameMatch) {
      return null;
    }

    let filename = filenameMatch[1];

    // Remove quotes
    if (filename.startsWith('"') && filename.endsWith('"')) {
      filename = filename.slice(1, -1);
    }

    // Handle URL encoding
    try {
      filename = decodeURIComponent(filename);
    } catch {
      // If decoding fails, use as is
    }

    return filename;
  }
}
