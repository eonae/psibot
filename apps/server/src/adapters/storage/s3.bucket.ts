/* eslint-disable no-console */
import * as fs from 'node:fs/promises';

import type { Bucket } from '../../core/ports';

import {
  GetObjectCommand,
  PutObjectCommand,
  S3Client,
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

export class S3Bucket implements Bucket {
  private s3Client: S3Client;
  private bucketName: string;

  constructor(
    endpointUrl: string,
    accessKeyId: string,
    secretAccessKey: string,
    bucketName: string,
  ) {
    this.s3Client = new S3Client({
      endpoint: endpointUrl,
      credentials: {
        accessKeyId: accessKeyId,
        secretAccessKey: secretAccessKey,
      },
      region: 'ru-central1',
      forcePathStyle: true, // Required for Yandex Cloud S3
    });
    this.bucketName = bucketName;
  }

  async upload(filePath: string, objectName?: string): Promise<void> {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const objectKey = objectName || filePath.split('/').pop()!;

    console.log(`📤 Uploading ${filePath} to ${this.bucketName}/${objectKey}`);

    const fileContent = await fs.readFile(filePath);

    const command = new PutObjectCommand({
      Bucket: this.bucketName,
      Key: objectKey,
      Body: fileContent,
    });

    await this.s3Client.send(command);

    console.log(`✅ Successfully uploaded ${objectKey}`);
  }

  async getPresignedUrl(objectName: string): Promise<string> {
    console.log(`🔗 Generating presigned URL for ${objectName}`);

    const command = new GetObjectCommand({
      Bucket: this.bucketName,
      Key: objectName,
    });

    // URL is valid for 1 hour
    const url = await getSignedUrl(this.s3Client, command, { expiresIn: 3600 });

    console.log(`✅ Presigned URL generated: ${url}`);
    return url;
  }
}
