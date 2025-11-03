import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

export interface TranscriptionSegment {
  start: number; // seconds
  end: number;
  text: string;
}

export class TranscriptionResult {
  segments: TranscriptionSegment[];

  constructor(segments: TranscriptionSegment[] = []) {
    this.segments = segments;
  }

  toString(): string {
    return this.segments
      .map((x) => `[${this.fmt(x.start)} - ${this.fmt(x.end)}] ${x.text}`)
      .join('\n');
  }

  private fmt(seconds: number): string {
    const totalMilliseconds = Math.floor(seconds * 1000);
    const hasHours = Math.floor(seconds / 3600) > 0;
    return dayjs
      .utc(totalMilliseconds)
      .format(hasHours ? 'H:mm:ss.SSS' : 'm:ss.SSS');
  }

  static parse(content: string): TranscriptionResult {
    const lines = content.trim().split('\n');
    const segments: TranscriptionSegment[] = [];

    for (const line of lines) {
      const match = line.match(/\[(.+?) - (.+?)]\s*(.*)/);
      if (match) {
        const [, startStr, endStr, text] = match;
        segments.push({
          start: this.parseTime(startStr),
          end: this.parseTime(endStr),
          text: text.trim(),
        });
      }
    }

    return new TranscriptionResult(segments);
  }

  private static parseTime(timeStr: string): number {
    const parts = timeStr.split(':').map(Number);
    if (parts.length === 3) {
      const [hours, minutes, seconds] = parts;
      return hours * 3600 + minutes * 60 + seconds;
    } else if (parts.length === 2) {
      const [minutes, seconds] = parts;
      return minutes * 60 + seconds;
    }

    return 0;
  }
}
