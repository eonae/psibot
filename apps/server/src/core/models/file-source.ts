export enum SourceType {
  DOWNLOADED_FILE_PATH = 'downloaded_file_path',
  UPLOAD_URL = 'upload_url',
  TELEGRAM_FILE_ID = 'telegram_file_id',
}

export interface FileSource {
  type: SourceType;
  value: string;
}
