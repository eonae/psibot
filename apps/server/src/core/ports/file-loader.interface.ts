import type { FileSource } from '../models/file-source.js';

export interface FileLoader {
  supports(source: FileSource): boolean;
  load(source: FileSource): Promise<Buffer>;
}
