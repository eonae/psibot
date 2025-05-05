import os
from pathlib import Path
from typing import Optional

import boto3  # type: ignore

from src.app.config import Config
from src.app.core.ports import Bucket


class S3Bucket(Bucket):
    def __init__(self, config: Config):
        self.bucket_name = config.YC_SPEECH_KIT_BUCKET_NAME
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=config.YC_S3_ENDPOINT,
            aws_access_key_id=config.YC_ACCESS_KEY_ID,
            aws_secret_access_key=config.YC_SECRET_ACCESS_KEY,
        )

    def upload(
        self, path: str | Path, object_name: Optional[str] = None
    ) -> None:
        if object_name is None:
            object_name = os.path.basename(path)

        return self.s3_client.upload_file(path, self.bucket_name, object_name)

    def get_presigned_url(self, object_name: str | Path) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": str(object_name)},
            ExpiresIn=3600,
        )
