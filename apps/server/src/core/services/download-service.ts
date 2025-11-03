/* eslint-disable no-console */

import type { TranscriptionJob } from '../models';
import type { FileLoader, FileStorage } from '../ports';

export class DownloadService {
  constructor(
    private loaders: FileLoader[],
    private storage: FileStorage,
  ) {}

  async download(job: TranscriptionJob): Promise<void> {
    console.log(`📥 Downloading file for job ${job.id}`);

    const loader = this.loaders.find((l) => l.supports(job.source));
    if (!loader) {
      throw new Error(`No loader found for source type: ${job.source.type}`);
    }

    const fileData = await loader.load(job.source);
    await this.storage.save(fileData, job.paths.original);

    job.toConverting();

    console.log(`✅ File downloaded and saved: ${job.paths.original}`);
  }
}
