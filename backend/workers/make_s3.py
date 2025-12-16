import os
import boto3
from dotenv import load_dotenv

load_dotenv()


ENDPOINT = os.getenv("S3_ENDPOINT", "https://storage.yandexcloud.net")
REGION = os.getenv("AWS_REGION", "ru-central1")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def _require_creds():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        raise RuntimeError(
            "Missing AWS credentials. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
            "(or lowercase equivalents) via environment variables or a .env file."
        )


def make_s3():
    """Create a configured S3 client for Yandex Object Storage.

    Raises:
        RuntimeError: if credentials are missing.
    """
    _require_creds()
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
