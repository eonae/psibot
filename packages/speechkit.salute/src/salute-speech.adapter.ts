/* eslint-disable no-console */

import crypto from 'node:crypto';
import * as fs from 'node:fs/promises';
import * as https from 'node:https';
import * as os from 'node:os';
import * as path from 'node:path';

import type { SpeechToText, TranscriptionSegment } from '@speechkit/core';
import { TranscriptionResult } from '@speechkit/core';
import axios from 'axios';
import ffmpeg from 'fluent-ffmpeg';
import FormData from 'form-data';

const SALUTE_BASE_URL = 'https://smartspeech.sber.ru/rest/v1';
const OAUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth';
const POLLING_INTERVAL = 5000; // 5 seconds
const TOKEN_REFRESH_THRESHOLD = 60_000; // Refresh token if less than 1 minute left

// HTTPS agent для обработки самоподписанных сертификатов
// ВНИМАНИЕ: Это снижает безопасность! Используйте только для разработки.
// В продакшене рекомендуется добавить сертификат в список доверенных.
const httpsAgent = new https.Agent({
  rejectUnauthorized: false, // Игнорируем ошибки SSL-сертификата
});

interface AccessTokenResponse {
  access_token: string;
  expires_at: number;
}

// Парсим время из формата "1.560s" или "0s"
const parseTime = (timeStr: string | undefined): number => {
  if (!timeStr) {
    return 0;
  }
  const match = timeStr.match(/([\d.]+)s?/);
  return match ? Number.parseFloat(match[1]) : 0;
};

export class SaluteSpeechAdapter implements SpeechToText {
  private authorizationKey: string;
  private scope: string;
  private accessToken: string | null = null;
  private tokenExpiresAt = 0;

  constructor(authorizationKey: string, scope: string) {
    this.authorizationKey = authorizationKey;
    this.scope = scope;
  }

  private async getAccessToken(): Promise<string> {
    // Проверяем, не истек ли токен (если осталось меньше минуты - обновляем)
    const now = Date.now();
    if (
      this.accessToken &&
      this.tokenExpiresAt - now > TOKEN_REFRESH_THRESHOLD
    ) {
      return this.accessToken;
    }

    console.log('🔑 Obtaining new access token from Salute Speech OAuth');

    const rqUID = crypto.randomUUID();
    const response = await axios.post<AccessTokenResponse>(
      OAUTH_URL,
      `scope=${encodeURIComponent(this.scope)}`,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Accept: 'application/json',
          RqUID: rqUID,
          Authorization: `Basic ${this.authorizationKey}`,
        },
        httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
        timeout: 10_000,
      },
    );

    this.accessToken = response.data.access_token;
    this.tokenExpiresAt = response.data.expires_at;

    console.log(
      `✅ Access token obtained, expires at: ${new Date(this.tokenExpiresAt).toISOString()}`,
    );

    return this.accessToken;
  }

  private async getHeaders(
    contentType?: string,
  ): Promise<Record<string, string>> {
    const token = await this.getAccessToken();
    const headers: Record<string, string> = {
      Authorization: `Bearer ${token}`,
    };
    if (contentType) {
      headers['Content-Type'] = contentType;
    }
    return headers;
  }

  async transcribe(audioPath: string): Promise<TranscriptionResult> {
    console.log(`🌎 Starting Salute Speech recognition for: ${audioPath}`);

    try {
      // Step 1: Upload audio file
      console.log(`🔼 Uploading file to Salute Speech: ${audioPath}`);
      const fileId = await this.uploadFile(audioPath);
      console.log(`🔗 File uploaded. File ID: ${fileId}`);

      // Step 2: Start async recognition
      console.log(`🌎 Sending async recognition request to Salute Speech`);
      const taskId = await this.startRecognition(fileId);
      console.log(`⏳ Recognition task created: ${taskId}`);

      // Step 3: Poll for task completion
      let taskCompleted = false;
      let attempts = 0;
      const maxAttempts = 120; // Максимум 10 минут (120 * 5 секунд)

      while (!taskCompleted && attempts < maxAttempts) {
        const status = await this.getTaskStatus(taskId);
        attempts++;

        if (status.done) {
          console.log(`✅ Recognition task completed: ${taskId}`);
          taskCompleted = true;

          if (status.error) {
            throw new Error(`Recognition task failed: ${status.error}`);
          }
        } else {
          console.log(
            `⏳ Waiting for recognition result: ${taskId} (attempt ${attempts}/${maxAttempts})`,
          );
          await this.sleep(POLLING_INTERVAL);
        }
      }

      if (!taskCompleted) {
        throw new Error(
          `Recognition task timeout after ${maxAttempts} attempts`,
        );
      }

      // Step 4: Get result file ID
      const resultFileId = await this.getResultFileId(taskId);
      if (!resultFileId) {
        throw new Error('No result file ID in task response');
      }

      // Step 5: Download and parse result
      console.log(`📦 Downloading recognition result: ${resultFileId}`);
      const result = await this.downloadResult(resultFileId);

      return this.parseResults(result);
    } catch (error) {
      console.error('❌ Error in Salute Speech recognition:', error);
      throw new Error(
        `Failed to transcribe with Salute Speech: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    }
  }

  private async uploadFile(filePath: string): Promise<string> {
    // Конвертируем входной файл в OGG Opus (моно) перед загрузкой
    const tempDir = await fs.mkdtemp(
      path.join(os.tmpdir(), 'speechkit-salute-'),
    );
    const opusPath = path.join(tempDir, 'audio.ogg');

    console.log('🔧 Converting input to OGG Opus (mono) for Salute upload');
    await new Promise<void>((resolve, reject) => {
      ffmpeg(filePath)
        .audioCodec('libopus')
        .audioChannels(1)
        .audioFrequency(48_000)
        .format('ogg')
        .on('end', () => resolve())
        .on('error', (err) => reject(err))
        .save(opusPath);
    });

    const audioData = await fs.readFile(opusPath);
    const fileName = path.basename(filePath).replace(/\.(wav|pcm)$/i, '.ogg');
    console.log(
      `📁 Preparing upload: name=${fileName}, size=${audioData.byteLength} bytes, contentType=audio/ogg;codecs=opus`,
    );

    // Use FormData for multipart upload
    const formData = new FormData();
    formData.append('data', audioData, {
      filename: fileName,
      contentType: 'audio/ogg;codecs=opus',
    });

    const headers = await this.getHeaders();
    const response = await axios.post(
      `${SALUTE_BASE_URL}/data:upload`,
      formData,
      {
        headers: {
          ...headers,
          ...formData.getHeaders(),
        },
        httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
        timeout: 60_000,
      },
    );

    console.log(
      `📨 Upload response status=${response.status}, content-type=${response.headers?.['content-type']}`,
    );
    console.log(
      '📨 Upload response body:',
      JSON.stringify(response.data, null, 2),
    );

    // API возвращает ответ в формате: { status: 200, result: { request_file_id: "..." } }
    const fileId =
      response.data.result?.request_file_id ||
      response.data.request_file_id ||
      response.data.file_id ||
      response.data.id ||
      response.data.data_id;

    if (!fileId || typeof fileId !== 'string') {
      throw new Error(
        `Failed to get file ID from upload response: ${JSON.stringify(response.data)}`,
      );
    }

    // Очистка временных файлов
    await fs.rm(tempDir, { recursive: true, force: true });

    return fileId;
  }

  private async startRecognition(fileId: string): Promise<string> {
    console.log(`🌎 Starting recognition for file: ${fileId}`);
    // Согласно документации SaluteSpeech API:
    // https://developers.sber.ru/docs/ru/salutespeech/rest/post-async-speech-recognition
    // Формат запроса должен содержать request_file_id и параметры распознавания
    // Согласно документации: https://developers.sber.ru/docs/ru/salutespeech/guides/recognition/encodings
    // PCM_S16LE для WAV с заголовком (16 кГц, моно, signed 16-bit little-endian)
    // API требует явного указания audio_encoding
    const data = {
      request_file_id: fileId,
      options: {
        model: 'general',
        language: 'ru-RU',
        audio_encoding: 'OPUS',
      },
    };

    console.log(
      '📤 Sending recognition request:',
      JSON.stringify(data, null, 2),
    );

    const headers = await this.getHeaders('application/json');
    const response = await axios.post(
      `${SALUTE_BASE_URL}/speech:async_recognize`,
      data,
      {
        headers,
        httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
        timeout: 10_000,
      },
    );

    // API возвращает ответ в формате: { status: 200, result: { task_id: "..." } }
    console.log(
      `📤 Recognition response status=${response.status}, content-type=${response.headers?.['content-type']}`,
    );
    console.log(
      '📤 Recognition task response:',
      JSON.stringify(response.data, null, 2),
    );

    const taskId =
      response.data.result?.task_id ||
      response.data.result?.id ||
      response.data.task_id ||
      response.data.id;

    if (!taskId || typeof taskId !== 'string') {
      throw new Error(
        `Failed to get task ID from recognition response: ${JSON.stringify(response.data)}`,
      );
    }

    return taskId;
  }

  private async getTaskStatus(
    taskId: string,
  ): Promise<{ done: boolean; error?: string }> {
    const headers = await this.getHeaders();
    const response = await axios.get(`${SALUTE_BASE_URL}/task:get`, {
      headers,
      params: { id: taskId },
      httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
      timeout: 10_000,
    });

    // API может возвращать ответ в формате: { status: 200, result: { status: "NEW"/"DONE"/"ERROR", ... } }
    const taskData = response.data.result || response.data;

    // Проверяем статус задачи: DONE, COMPLETED, SUCCESS означают завершение
    // NEW, PROCESSING, IN_PROGRESS означают, что задача ещё выполняется
    const taskStatus = (taskData.status || taskData.state || '').toUpperCase();
    const isDone =
      taskStatus === 'DONE' ||
      taskStatus === 'COMPLETED' ||
      taskStatus === 'SUCCESS' ||
      taskStatus === 'FINISHED' ||
      taskData.done === true;

    const hasError =
      taskStatus === 'ERROR' || taskStatus === 'FAILED' || taskData.error;

    console.log(
      `📊 Task status: status=${taskStatus}, done=${isDone}, hasError=${!!hasError}`,
    );

    return {
      done: isDone,
      error: hasError
        ? taskData.error?.message || taskData.error || 'Task failed'
        : undefined,
    };
  }

  private async getResultFileId(taskId: string): Promise<string | null> {
    const headers = await this.getHeaders();
    const response = await axios.get(`${SALUTE_BASE_URL}/task:get`, {
      headers,
      params: { id: taskId },
      httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
      timeout: 10_000,
    });

    console.log(
      '📋 Task status response:',
      JSON.stringify(response.data, null, 2),
    );

    // API может возвращать ответ в формате: { status: 200, result: { response_file_id: "..." } }
    const taskData = response.data.result || response.data;

    // API may return response_file_id or file_id
    const fileId =
      taskData.response_file_id ||
      taskData.file_id ||
      taskData.result?.response_file_id ||
      taskData.result?.file_id ||
      null;

    console.log(`📋 Extracted file ID: ${fileId}`);

    return fileId;
  }

  private async downloadResult(fileId: string): Promise<unknown> {
    const headers = await this.getHeaders();
    const response = await axios.get<string>(
      `${SALUTE_BASE_URL}/data:download`,
      {
        headers,
        params: { response_file_id: fileId },
        httpsAgent, // Используем httpsAgent для игнорирования ошибок SSL
        timeout: 30_000,
        responseType: 'text',
      },
    );
    const contentType = response.headers?.['content-type'] || '';
    const bodyText = response.data || '';
    console.log(
      `📥 Download response: content-type=${contentType}, length=${bodyText.length}`,
    );
    console.log('📥 Body preview:', bodyText.slice(0, 500));

    // Пытаемся распарсить как JSON, иначе отдаём как простой текст
    try {
      const parsed = JSON.parse(bodyText);
      const resultData =
        typeof parsed === 'object' && parsed !== null && (parsed as any).result
          ? (parsed as any).result
          : parsed;
      console.log(
        '📥 Parsed JSON result keys:',
        typeof resultData === 'object' && resultData !== null
          ? Object.keys(resultData as any)
          : [],
      );
      return resultData;
    } catch {
      console.log('📥 Non-JSON result, returning plain text payload');
      return { text: bodyText };
    }
  }

  private parseResults(raw: unknown): TranscriptionResult {
    console.log('🔍 Parsing results, raw data type:', typeof raw);
    console.log('🔍 Parsing results, raw data:', JSON.stringify(raw, null, 2));

    const segments: TranscriptionSegment[] = [];

    // Type guard to check if raw is an object or array
    if (typeof raw !== 'object' || raw === null) {
      console.log('⚠️ Raw data is not an object, returning empty result');
      return new TranscriptionResult(segments);
    }

    // Format 0: Array of objects with results array (SaluteSpeech API format)
    if (Array.isArray(raw)) {
      console.log('📋 Processing array format with', raw.length, 'items');
      for (const item of raw) {
        if (typeof item === 'object' && item !== null) {
          const itemData = item as Record<string, unknown>;
          if (Array.isArray(itemData.results)) {
            console.log(
              '📋 Found results array with',
              itemData.results.length,
              'items',
            );
            for (const result of itemData.results) {
              const r = result as Record<string, unknown>;
              const text =
                (r.text as string) || (r.normalized_text as string) || '';

              // Пропускаем пустые тексты
              if (!text || text.trim() === '') {
                continue;
              }

              const start = parseTime(r.start as string);
              const end = parseTime(r.end as string);

              segments.push({
                start,
                end: end || start,
                text: text.trim(),
              });
            }
          }
        }
      }

      if (segments.length > 0) {
        console.log(
          `✅ Parsed ${segments.length} segments from SaluteSpeech array format`,
        );
        return new TranscriptionResult(segments);
      }
    }

    const data = raw as Record<string, unknown>;
    console.log('🔍 Parsing data keys:', Object.keys(data));

    // Salute Speech API may return results in different formats
    // Try to handle various response structures

    // Format 1: Direct segments array
    if (Array.isArray(data.segments)) {
      for (const segment of data.segments) {
        const seg = segment as Record<string, unknown>;
        segments.push({
          start: (seg.start as number) || (seg.start_time as number) || 0,
          end: (seg.end as number) || (seg.end_time as number) || 0,
          text: (seg.text as string) || (seg.word as string) || '',
        });
      }
    }
    // Format 2: Words array
    else if (Array.isArray(data.words)) {
      for (const word of data.words) {
        const w = word as Record<string, unknown>;
        segments.push({
          start: (w.start as number) || (w.start_time as number) || 0,
          end: (w.end as number) || (w.end_time as number) || 0,
          text: (w.text as string) || (w.word as string) || '',
        });
      }
    }
    // Format 3: Nested structure
    else if (
      data.result &&
      typeof data.result === 'object' &&
      data.result !== null
    ) {
      const result = data.result as Record<string, unknown>;
      if (Array.isArray(result.words)) {
        for (const word of result.words) {
          const w = word as Record<string, unknown>;
          segments.push({
            start:
              Number.parseFloat(
                (w.start_time_ms as string) || String(w.start || 0),
              ) / 1000,
            end:
              Number.parseFloat(
                (w.end_time_ms as string) || String(w.end || 0),
              ) / 1000,
            text: (w.text as string) || (w.word as string) || '',
          });
        }
      }
    }
    // Format 4: Text with timestamps
    else if (data.text && Array.isArray(data.alternatives)) {
      for (const alt of data.alternatives) {
        const alternative = alt as Record<string, unknown>;
        if (Array.isArray(alternative.words)) {
          for (const word of alternative.words) {
            const w = word as Record<string, unknown>;
            segments.push({
              start:
                Number.parseFloat(
                  (w.startTimeMs as string) ||
                    (w.start_time_ms as string) ||
                    String(w.start || 0),
                ) / 1000,
              end:
                Number.parseFloat(
                  (w.endTimeMs as string) ||
                    (w.end_time_ms as string) ||
                    String(w.end || 0),
                ) / 1000,
              text: (w.text as string) || (w.word as string) || '',
            });
          }
        }
      }
    }
    // Format 5: Simple text (no timestamps)
    else if (data.text && typeof data.text === 'string') {
      segments.push({
        start: 0,
        end: 0,
        text: data.text,
      });
    }

    console.log(
      `✅ Parsed ${segments.length} segments from SaluteSpeech response`,
    );
    if (segments.length > 0) {
      console.log(`📝 First segment:`, segments[0]);
      if (segments.length > 1) {
        console.log(`📝 Last segment:`, segments.at(-1));
      }
    } else {
      console.log('⚠️ No segments extracted from response!');
    }

    return new TranscriptionResult(segments);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
