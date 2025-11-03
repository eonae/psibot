/* eslint-disable no-console */

import type { SpeechToText, TranscriptionSegment } from '@speechkit/core';
import { TranscriptionResult } from '@speechkit/core';
import axios from 'axios';

const STT_BASE_URL = 'https://stt.api.cloud.yandex.net/stt/v3';
const OPERATIONS_BASE_URL = 'https://operation.api.cloud.yandex.net/operations';
const POLLING_INTERVAL = 5000; // 5 seconds

export class YandexSpeechKitAdapter implements SpeechToText {
  private apiKey: string;
  private bucket: any; // Will be properly typed when S3Bucket is implemented

  constructor(apiKey: string, bucket: any) {
    this.apiKey = apiKey;
    this.bucket = bucket;
  }

  private getHeaders(): Record<string, string> {
    return {
      Authorization: `Api-Key ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  async transcribe(audioPath: string): Promise<TranscriptionResult> {
    console.log(`🔼 Uploading file to storage: ${audioPath}`);

    // Extract just the filename from the path for the object key
    const filename = audioPath.split('/').pop() || audioPath;
    const objectKey = `${filename}_${Date.now()}`;
    await this.bucket.upload(audioPath, objectKey);

    const url = await this.bucket.getPresignedUrl(objectKey);
    console.log(`🔗 File is uploaded to storage. Presigned URL: ${url}`);

    console.log('🌎 Sending async recognition request to Yandex SpeechKit');
    const operationId = await this.recognizeFileAsync(url);
    console.log(`⏳ Operation created: ${operationId}`);

    for (;;) {
      const done = await this.getOperationStatus(operationId);
      if (done) {
        console.log(`✅ Operation completed: ${operationId}`);
        break;
      }

      console.log(`⏳ Waiting for operation result: ${operationId}`);
      await this.sleep(POLLING_INTERVAL);
    }

    console.log(`📦 Fetching recognition result: ${operationId}`);
    const rawResults = await this.getRecognition(operationId);

    return this.parseResults(rawResults);
  }

  private async recognizeFileAsync(s3Url: string): Promise<string> {
    const url = `${STT_BASE_URL}/recognizeFileAsync`;
    const data = {
      uri: s3Url,
      recognition_model: {
        model: 'general',
        audio_processing_type: 'FULL_DATA',
        audio_format: {
          container_audio: {
            container_audio_type: 'WAV',
          },
        },
        language_restriction: {
          restriction_type: 'WHITELIST',
          language_codes: ['ru-RU'], // Changed from en-EN to ru-RU
        },
      },
    };

    const response = await axios.post(url, data, {
      headers: this.getHeaders(),
      timeout: 10_000,
    });

    return response.data.id;
  }

  private async getOperationStatus(operationId: string): Promise<boolean> {
    const url = `${OPERATIONS_BASE_URL}/${operationId}`;

    const response = await axios.get(url, {
      headers: this.getHeaders(),
      timeout: 10_000,
    });

    return response.data.done;
  }

  private async getRecognition(operationId: string): Promise<any[]> {
    const url = `${STT_BASE_URL}/getRecognition`;
    const params = { operation_id: operationId };

    const response = await axios.get(url, {
      headers: this.getHeaders(),
      params,
      timeout: 10_000,
      responseType: 'stream',
    });

    const results: any[] = [];

    for await (const chunk of response.data) {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          try {
            const result = JSON.parse(line);
            if (result.result?.final) {
              results.push(result);
            }
          } catch (error) {
            console.warn('Failed to parse JSON:', error);
          }
        }
      }
    }

    return results;
  }

  private parseResults(raw: any[]): TranscriptionResult {
    const segments: TranscriptionSegment[] = [];

    for (const chunk of raw) {
      if (!chunk.result?.final) {
        continue;
      }

      const final = chunk.result.final;
      if (!final.alternatives) {
        continue;
      }

      for (const alternative of final.alternatives) {
        if (
          !alternative.text ||
          !alternative.startTimeMs ||
          !alternative.endTimeMs
        ) {
          continue;
        }

        segments.push({
          start: Number.parseFloat(alternative.startTimeMs) / 1000,
          end: Number.parseFloat(alternative.endTimeMs) / 1000,
          text: alternative.text,
        });
      }
    }

    return new TranscriptionResult(segments);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
