/* eslint-disable no-console */

import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';

import type { TranscriptionJob } from '../models';
import type { FileStorage } from '../ports';

import ffmpeg from 'fluent-ffmpeg';

export class ConversionService {
  constructor(private storage: FileStorage) {}

  async convert(job: TranscriptionJob): Promise<void> {
    console.log(`🔄 Converting audio to WAV for job ${job.id}`);

    // Read original file from storage
    const originalData = await this.storage.read(job.paths.original);

    // Create temporary files
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'speechkit-'));
    const inputPath = path.join(tempDir, 'input');
    const outputPath = path.join(tempDir, 'output.wav');

    try {
      // Write input file
      await fs.writeFile(inputPath, new Uint8Array(originalData));

      // Convert to WAV
      await new Promise<void>((resolve, reject) => {
        ffmpeg(inputPath)
          .audioCodec('pcm_s16le')
          .toFormat('wav')
          // Нормализация громкости и удаление лидинг/трейлинг тишины
          .audioFilter('loudnorm=I=-16:TP=-1.5:LRA=11')
          .audioFilter(
            'silenceremove=start_periods=1:start_duration=0.3:start_threshold=-50dB:stop_periods=1:stop_duration=0.3:stop_threshold=-50dB',
          )
          .audioChannels(1)
          .audioFrequency(16_000)
          .on('end', () => resolve())
          .on('error', (err) => reject(err))
          .save(outputPath);
      });

      // Probe converted file to verify format/params
      const probeInfo = await new Promise<ffmpeg.FfprobeData>(
        (resolve, reject) => {
          ffmpeg.ffprobe(outputPath, (err, data) => {
            if (err) {
              return reject(err);
            }
            resolve(data);
          });
        },
      );

      const formatName = probeInfo.format?.format_name || '';
      const sampleRate = Number(
        (probeInfo.streams?.[0]?.sample_rate as unknown) || 0,
      );
      const channels = probeInfo.streams?.[0]?.channels || 0;
      const codecName = probeInfo.streams?.[0]?.codec_name || '';

      console.log({ formatName, sampleRate, channels, codecName });

      const isWav =
        typeof formatName === 'string' && formatName.includes('wav');
      const is16k = sampleRate === 16_000;
      const isMono = channels === 1;
      const isPcmS16le = codecName === 'pcm_s16le';

      if (!isWav || !is16k || !isMono || !isPcmS16le) {
        throw new Error(
          `Converted file has unexpected format: format=${formatName}, codec=${codecName}, rate=${sampleRate}, channels=${channels}. Expected: WAV/pcm_s16le/16000Hz/1ch`,
        );
      }

      // Read converted file
      const convertedData = await fs.readFile(outputPath);

      // Save to storage
      await this.storage.save(convertedData, job.paths.wav);

      job.toTranscribing();

      console.log(`✅ Audio converted to WAV: ${job.paths.wav}`);
    } finally {
      // Cleanup temporary files
      await fs.rm(tempDir, { recursive: true, force: true });
    }
  }
}
