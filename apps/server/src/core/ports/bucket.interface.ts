export interface Bucket {
  upload(filePath: string, objectName?: string): Promise<void>;
  getPresignedUrl(objectName: string): Promise<string>;
}
