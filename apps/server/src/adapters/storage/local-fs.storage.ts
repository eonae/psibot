import * as fs from 'node:fs/promises';
import * as path from 'node:path';

import type { FileStorage } from '../../core/ports';

export class LocalFileStorage implements FileStorage {
  private basePath: string;

  constructor(basePath: string) {
    this.basePath = basePath;
  }

  async save(data: Buffer, filePath: string): Promise<void> {
    const fullPath = path.join(this.basePath, filePath);
    await fs.mkdir(path.dirname(fullPath), { recursive: true });
    await fs.writeFile(fullPath, new Uint8Array(data));
  }

  async read(filePath: string): Promise<Buffer> {
    const fullPath = path.join(this.basePath, filePath);
    return await fs.readFile(fullPath);
  }

  async delete(filePath: string): Promise<void> {
    const fullPath = path.join(this.basePath, filePath);
    await fs.unlink(fullPath);
  }

  async exists(filePath: string): Promise<boolean> {
    const fullPath = path.join(this.basePath, filePath);
    try {
      await fs.access(fullPath);
      return true;
    } catch {
      return false;
    }
  }
}
