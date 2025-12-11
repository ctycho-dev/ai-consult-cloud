# s3_client.py — Class wrapper for Yandex Object Storage (S3-compatible).
from __future__ import annotations
import os
import mimetypes
from pathlib import Path
from typing import Generator, Iterable

import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


class YandexS3Client:
    """High-level S3 client for Yandex Object Storage.

    Creates the connection in __init__ and exposes convenience methods.
    Raises RuntimeError if credentials are missing.

    Env vars (UPPERCASE and lowercase are both supported):
        AWS_ACCESS_KEY_ID / aws_access_key_id
        AWS_SECRET_ACCESS_KEY / aws_secret_access_key
        AWS_REGION / aws_region (default: ru-central1)
        S3_ENDPOINT / s3_endpoint (default: https://storage.yandexcloud.net)
    """

    def __init__(self) -> None:

        self.endpoint = settings.S3_ENDPOINT
        self.region = settings.AWS_REGION
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY

        self._s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    # -------- Bucket ops --------
    def list_buckets(self) -> Iterable[dict]:
        """Return a list of buckets (requires permissions)."""
        # resp = s3.list_buckets()
        # buckets = resp.get("Buckets", [])
        return self._s3.list_buckets().get("Buckets", [])

    def head_bucket(self, bucket: str) -> None:
        """Raise if bucket doesn't exist or access is denied."""
        self._s3.head_bucket(Bucket=bucket)

    # -------- Object ops --------
    # def list_objects(self, bucket: str, prefix: str = "") -> Generator[Dict, None, None]:
    #     """Yield object summaries for a bucket (optionally filtered by prefix)."""
    #     paginator = self._s3.get_paginator("list_objects_v2")
    #     for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    #         for obj in page.get("Contents", []):
    #             yield obj

    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:

        ans = []
        self._s3.head_bucket(Bucket=bucket)

        paginator = self._s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        for page in pages:
            ans.extend(page.get("Contents", []))
        return ans

    def upload_file(
        self,
        bucket: str,
        local_path: str | os.PathLike,
        key: str,
        public: bool = False,
        content_type: str | None = None,
        extra_args: dict | None = None,
    ) -> None:
        """Upload local file to s3://bucket/key.

        Args:
            bucket: Destination bucket.
            local_path: Path to local file.
            key: Destination key. Defaults to file name.
            public: If True, sets ACL public-read (bucket policy must allow).
            content_type: Override Content-Type header; guessed from key if not provided.
            extra_args: ExtraArgs dict passed to boto3 upload_file.
        """
        path = Path(local_path)
        if not path.is_file():
            raise FileNotFoundError(f"Not a file: {path}")

        key = key or path.name
        args = dict(extra_args or {})

        if content_type:
            args.setdefault("ContentType", content_type)
        else:
            guessed, _ = mimetypes.guess_type(key)
            if guessed:
                args.setdefault("ContentType", guessed)

        if public:
            args.setdefault("ACL", "public-read")

        self._s3.upload_file(str(path), bucket, key, ExtraArgs=args)

    def download_file(
        self,
        bucket: str,
        key: str,
        dest_path: str | os.PathLike
    ) -> None:
        """Download s3://bucket/key to dest_path (directory or file)."""
        dest = Path(dest_path)
        # If dest is a directory (or ends with slash), append filename from key
        if str(dest).endswith(os.sep) or (dest.exists() and dest.is_dir()):
            dest = dest / Path(key).name
        dest.parent.mkdir(parents=True, exist_ok=True)

        self._s3.download_file(bucket, key, str(dest))

    def delete_file(self, bucket: str, key: str, version_id: str | None = None) -> dict:
        """Delete object (or a specific version). Returns boto3 response."""
        kwargs = {"Bucket": bucket, "Key": key}
        if version_id:
            kwargs["VersionId"] = version_id
        return self._s3.delete_object(**kwargs)

    def object_exists(self, bucket: str, key: str, version_id: str | None = None) -> bool:
        """Check if an object (or version) exists."""
        try:
            kwargs = {"Bucket": bucket, "Key": key}
            if version_id:
                kwargs["VersionId"] = version_id
            self._s3.head_object(**kwargs)
            return True
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchKey"):
                return False
            raise

    # -------- Optional helpers --------
    def public_url(self, bucket: str, key: str) -> str:
        """Return the public HTTPS URL (works if object/bucket is public)."""
        return f"https://storage.yandexcloud.net/{bucket}/{key}"

    def presign_get(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        """Return a pre-signed GET URL valid for `expires_in` seconds."""
        return self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def presign_put(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        """Return a pre-signed PUT URL valid for `expires_in` seconds."""
        return self._s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_object_metadata(self, bucket: str, key: str) -> dict:
        """
        Get object metadata (size, content-type, etag, etc.) without downloading.
        
        Returns:
            dict with keys: ContentLength, ContentType, ETag, LastModified, etc.
        
        Raises:
            ClientError: If object doesn't exist or access denied.
        """
        return self._s3.head_object(Bucket=bucket, Key=key)
