/* eslint-disable no-console */

import { delay, Timespan } from '@rsdk/common';
import type { SpeechToText, TranscriptionSegment } from '@speechkit/core';
import { TranscriptionResult } from '@speechkit/core';
import type { AxiosInstance } from 'axios';
import axios from 'axios';

const STT_BASE_URL = 'https://stt.api.cloud.yandex.net/stt/v3';
const OPERATIONS_BASE_URL = 'https://operation.api.cloud.yandex.net/operations';
const POLLING_INTERVAL = new Timespan(5, 's');
const HTTP_TIMEOUT = new Timespan(10, 's');

export interface S3Bucket {
  upload(path: string, key: string): Promise<void>;
  getPresignedUrl(key: string): Promise<string>;
}

export class YandexSpeechKitAdapter implements SpeechToText {
  private operationsApi: AxiosInstance;
  private sttApi: AxiosInstance;
  private bucket: S3Bucket;

  constructor(apiKey: string, bucket: S3Bucket) {
    this.operationsApi = this.makeClient(OPERATIONS_BASE_URL, apiKey);
    this.sttApi = this.makeClient(STT_BASE_URL, apiKey);
    this.bucket = bucket;
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
      await delay(POLLING_INTERVAL);
    }

    console.log(`📦 Fetching recognition result: ${operationId}`);
    const rawResults = await this.getRecognition(operationId);

    return this.parseResults(rawResults);
  }

  private async recognizeFileAsync(s3Url: string): Promise<string> {
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

    const response = await this.sttApi.post('/recognizeFileAsync', data);

    return response.data.id;
  }

  private async getOperationStatus(operationId: string): Promise<boolean> {
    const { data } = await this.operationsApi.get(operationId);

    return data.done;
  }

  private async getRecognition(operationId: string): Promise<any[]> {
    const response = await this.sttApi.get('/getRecognition', {
      params: { operation_id: operationId },
      responseType: 'stream',
    });

    const results: any[] = [];

    for await (const chunk of response.data) {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (!line.trim()) {
          continue;
        }

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

      for (const { text, startTimeMs, endTimeMs } of final.alternatives) {
        if (!text || !startTimeMs || !endTimeMs) {
          continue;
        }

        segments.push({
          start: Number.parseFloat(startTimeMs) / 1000,
          end: Number.parseFloat(endTimeMs) / 1000,
          text,
        });
      }
    }

    return new TranscriptionResult(segments);
  }

  private makeClient(baseURL: string, apiKey: string): AxiosInstance {
    return axios.create({
      baseURL,
      headers: {
        Authorization: `Api-Key ${apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: HTTP_TIMEOUT.millis(),
    });
  }
}
