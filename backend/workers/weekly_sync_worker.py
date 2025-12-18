#!/usr/bin/env python3
"""
Weekly S3 reconciliation worker.
Scans S3 for files modified/deleted in last 10 days and syncs to backend.
With versioning enabled, tracks both creates and deletes.
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
LOOKBACK_DAYS = 2
BATCH_SIZE = 15
RATE_LIMIT_DELAY = 1


@log_timing("weekly_sync")
async def weekly_sync():
    """
    Weekly reconciliation: scan S3 for files modified/deleted in last 10 days
    and send events for any that might have been missed by webhooks.
    """
    logger.info(f"Starting weekly S3 reconciliation (last {LOOKBACK_DAYS} days)")
    
    s3 = make_s3()
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except ClientError as e:
        logger.error(f"Cannot access S3 bucket {S3_BUCKET}: {e}")
        return
    
    # Check if versioning is enabled
    try:
        versioning = s3.get_bucket_versioning(Bucket=S3_BUCKET)
        versioning_enabled = versioning.get('Status') == 'Enabled'
    except ClientError:
        versioning_enabled = False
    
    if versioning_enabled:
        logger.info("✅ Versioning enabled - tracking creates AND deletes")
        recent_activity = await scan_with_versioning(s3, cutoff_time)
    else:
        logger.warning("⚠️ Versioning disabled - tracking creates only")
        recent_activity = await scan_without_versioning(s3, cutoff_time)
    
    create_events = [e for e in recent_activity if e["action"] == "create"]
    delete_events = [e for e in recent_activity if e["action"] == "delete"]
    
    logger.info(
        f"Found {len(recent_activity)} events: "
        f"{len(create_events)} creates, {len(delete_events)} deletes"
    )
    
    if not recent_activity:
        logger.info("No recent activity to sync")
        return
    
    # Send events to backend
    await send_events_to_backend(create_events, delete_events)


async def scan_without_versioning(s3, cutoff_time: datetime) -> list:
    """Scan S3 without versioning (creates only)"""
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=S3_BUCKET,
        Prefix=S3_PREFIX,
        PaginationConfig={"PageSize": 1000}
    )
    
    recent_files = []
    total_scanned = 0
    
    for page in pages:
        for obj in page.get("Contents", []):
            total_scanned += 1
            key = obj["Key"]
            last_modified = obj["LastModified"]
            
            extension = Path(key).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                continue
            
            if last_modified > cutoff_time:
                recent_files.append({
                    "key": key,
                    "action": "create",
                    "timestamp": last_modified.isoformat()
                })
    
    logger.info(f"Scanned {total_scanned} objects (without versioning)")
    return recent_files


async def scan_with_versioning(s3, cutoff_time: datetime) -> list:
    """Scan S3 with versioning (creates + deletes)"""
    paginator = s3.get_paginator("list_object_versions")
    pages = paginator.paginate(
        Bucket=S3_BUCKET,
        Prefix=S3_PREFIX,
        PaginationConfig={"PageSize": 1000}
    )
    
    recent_activity = []
    total_scanned = 0
    
    for page in pages:
        # Process file versions (creates/modifies)
        for version in page.get("Versions", []):
            total_scanned += 1
            key = version["Key"]
            last_modified = version["LastModified"]
            is_latest = version.get("IsLatest", False)
            
            if not is_latest:
                continue
            
            extension = Path(key).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                continue
            
            if last_modified > cutoff_time:
                recent_activity.append({
                    "key": key,
                    "action": "create",
                    "timestamp": last_modified.isoformat()
                })
        
        # Process delete markers (deletions)
        for marker in page.get("DeleteMarkers", []):
            total_scanned += 1
            key = marker["Key"]
            last_modified = marker["LastModified"]
            is_latest = marker.get("IsLatest", False)
            
            if not is_latest:
                continue
            
            extension = Path(key).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                continue
            
            if last_modified > cutoff_time:
                recent_activity.append({
                    "key": key,
                    "action": "delete",
                    "timestamp": last_modified.isoformat()
                })
    
    logger.info(f"Scanned {total_scanned} objects (with versioning)")
    return recent_activity


async def send_events_to_backend(create_events: list, delete_events: list):
    """Send create and delete events to backend API"""
    headers = {
        "X-Webhook-Token": WEBHOOK_TOKEN,
        "Content-Type": "application/json"
    }
    
    uploaded = 0
    failed = 0
    
    async with aiohttp.ClientSession() as session:
        # Send create events
        if create_events:
            logger.info(f"Sending {len(create_events)} create events...")
            stats = await send_event_batch(
                session, headers, create_events, "ObjectCreate"
            )
            uploaded += stats["uploaded"]
            failed += stats["failed"]
        
        # Send delete events
        if delete_events:
            logger.info(f"Sending {len(delete_events)} delete events...")
            stats = await send_event_batch(
                session, headers, delete_events, "ObjectDelete"
            )
            uploaded += stats["uploaded"]
            failed += stats["failed"]
    
    logger.info(
        f"Weekly sync complete: {uploaded} uploaded, {failed} failed"
    )


async def send_event_batch(
    session: aiohttp.ClientSession,
    headers: dict,
    events: list,
    event_type: str
) -> dict:
    """Send a batch of events to backend"""
    uploaded = 0
    failed = 0
    
    # Map event type to Yandex Cloud format
    yandex_event_type = (
        "yandex.cloud.events.storage.ObjectCreate"
        if event_type == "ObjectCreate"
        else "yandex.cloud.events.storage.ObjectDelete"
    )
    
    for i in range(0, len(events), BATCH_SIZE):
        batch = events[i:i + BATCH_SIZE]
        
        # Create event payloads
        messages = []
        for idx, file_data in enumerate(batch):
            messages.append({
                "event_metadata": {
                    "event_type": yandex_event_type,
                    "event_id": f"weekly_sync_{event_type}_{i}_{idx}",
                    "created_at": file_data["timestamp"],
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
                json={"messages": messages},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    uploaded += len(messages)
                    logger.info(
                        f"✅ Sent batch of {len(messages)} {event_type} events"
                    )
                else:
                    failed += len(messages)
                    error = await resp.text()
                    logger.error(
                        f"❌ Failed to send {event_type} batch: "
                        f"{resp.status} - {error}"
                    )
        except Exception as e:
            failed += len(messages)
            logger.error(f"❌ Error sending {event_type} batch: {e}")
        
        # Rate limiting
        if i + BATCH_SIZE < len(events):
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return {"uploaded": uploaded, "failed": failed}


if __name__ == "__main__":
    asyncio.run(weekly_sync())
