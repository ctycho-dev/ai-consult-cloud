#!/usr/bin/env python3
"""
Weekly S3 reconciliation worker.
Scans S3 for files modified in last 10 days and syncs missing files to backend.
"""

import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logger import get_logger
from .decorator import log_timing
from .make_s3 import make_s3


logger = get_logger()

ALLOWED_EXTENSIONS = {'.pdf', '.xls', '.xlsx', '.xlsm', '.doc', '.docx'}
API_URL = f"{settings.BASE_URL}/api/v1/file/yandex/storage-event"
WEBHOOK_TOKEN = settings.YANDEX_WEBHOOK_TOKEN.get_secret_value()
S3_BUCKET = 'bitrix-sync'
S3_PREFIX = ''
BATCH_SIZE = 15
RATE_LIMIT_DELAY = 3


@log_timing("weekly_sync")
async def weekly_sync():
    """
    Weekly reconciliation: scan S3 for files modified in last 10 days
    and send events for any that might have been missed by webhooks.
    """
    logger.info("Starting weekly S3 reconciliation (last 10 days)")
    
    s3 = make_s3()
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=10)
    
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except ClientError as e:
        logger.error(f"Cannot access S3 bucket {S3_BUCKET}: {e}")
        return

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=S3_BUCKET,
        Prefix=S3_PREFIX,
        PaginationConfig={"PageSize": 1000}
    )

    recent_files = []
    total_scanned = 0

    # Scan S3 for recent files
    for page in pages:
        for obj in page.get("Contents", []):
            total_scanned += 1
            key = obj["Key"]
            last_modified = obj["LastModified"]

            # Filter by extension
            extension = Path(key).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                continue

            # Check if modified within timeframe
            if last_modified > cutoff_time:
                recent_files.append({
                    "key": key,
                    "last_modified": last_modified.isoformat()
                })

    logger.info(
        f"Scanned {total_scanned} S3 objects, "
        f"found {len(recent_files)} recent files (last 10 days)"
    )

    if not recent_files:
        logger.info("No recent files to sync")
        return

    # Send events in batches
    headers = {
        "X-Webhook-Token": WEBHOOK_TOKEN,
        "Content-Type": "application/json"
    }

    uploaded = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(recent_files), BATCH_SIZE):
            batch = recent_files[i:i + BATCH_SIZE]

            # Create events
            events = []
            for file_data in batch:
                events.append({
                    "event_metadata": {
                        "event_type": "yandex.cloud.events.storage.ObjectCreate",
                        "event_id": f"weekly_sync_{i}_{uploaded}",
                        "created_at": file_data["last_modified"],
                        "cloud_id": "b1gmipdpfo5db1mp8t2b",
                        "folder_id": "b1gafc0lslmrijqnkoja"
                    },
                    "details": {
                        "bucket_id": S3_BUCKET,
                        "object_id": file_data["key"]
                    }
                })
            
            try:
                async with session.post(
                    API_URL,
                    json={"messages": events},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        uploaded += len(events)
                        logger.info(f"Sent batch of {len(events)} events")
                    else:
                        failed += len(events)
                        error = await resp.text()
                        logger.error(f"Failed to send batch: {resp.status} - {error}")
            except Exception as e:
                failed += len(events)
                logger.error(f"Error sending batch: {e}")
            
            # Rate limiting
            if i + BATCH_SIZE < len(recent_files):
                await asyncio.sleep(RATE_LIMIT_DELAY)
    
    logger.info(
        f"Weekly sync complete: {uploaded} uploaded, {failed} failed"
    )


if __name__ == "__main__":
    asyncio.run(weekly_sync())
