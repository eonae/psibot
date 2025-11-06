import * as dotenv from 'dotenv';

dotenv.config();

export class Config {
  readonly TELEGRAM_BOT_TOKEN = this.mustLoad('TELEGRAM_BOT_TOKEN');

  readonly YC_API_KEY = this.mustLoad('YC_API_KEY');
  readonly YC_FOLDER_ID = this.mustLoad('YC_FOLDER_ID');
  readonly YC_S3_ENDPOINT = this.mustLoad('YC_S3_ENDPOINT');
  readonly YC_ACCESS_KEY_ID = this.mustLoad('YC_ACCESS_KEY_ID');
  readonly YC_SECRET_ACCESS_KEY = this.mustLoad('YC_SECRET_ACCESS_KEY');
  readonly YC_SPEECH_KIT_BUCKET_NAME =
    process.env.YC_SPEECH_KIT_BUCKET_NAME || 'speech-kit-wav';

  readonly SALUTE_SPEECH_AUTH_KEY = this.mustLoad('SALUTE_SPEECH_AUTH_KEY');
  readonly SALUTE_SPEECH_SCOPE = this.mustLoad('SALUTE_SPEECH_SCOPE');

  readonly OPENROUTER_API_KEY = this.mustLoad('OPENROUTER_API_KEY');

  readonly TEMPORAL_ADDRESS = this.mustLoad('TEMPORAL_ADDRESS');

  readonly STORAGE_PATH = process.env.STORAGE_PATH || './audio';
  readonly PORT = Number.parseInt(process.env.PORT || '8000', 10);

  private mustLoad(key: string): string {
    const value = process.env[key];
    if (!value) {
      throw new Error(`${key} is not set in environment`);
    }
    return value;
  }
}
