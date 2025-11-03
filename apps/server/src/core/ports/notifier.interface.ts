export interface Notifier {
  notify(userId: number, message: string): Promise<void>;
  sendDocument(
    userId: number,
    file: Buffer,
    filename: string,
    caption: string,
  ): Promise<void>;
  sendProgress(userId: number, message: string): Promise<void>;
}
