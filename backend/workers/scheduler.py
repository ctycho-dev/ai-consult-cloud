import asyncio
from datetime import datetime, timedelta
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# from workers.upload_worker import process_upload_batch
from workers.indexing_worker import check_indexing_status
from workers.upload_worker import process_upload_batch
from workers.delete_worker import process_deletions
from workers.weekly_sync_worker import weekly_sync


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Quiet down noisy loggers
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    logger = logging.getLogger('app.scheduler')
    logger.info("🚀 Scheduler starting...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler(event_loop=loop)

    now = datetime.now()

    # Worker 1: Upload to OpenAI every 2 minutes
    scheduler.add_job(
        process_upload_batch,
        IntervalTrigger(minutes=3),
        id='upload_worker',
        max_instances=1,
        next_run_time=now
    )

    # Worker 2: Check indexing status every 2 minutes
    scheduler.add_job(
        check_indexing_status,
        IntervalTrigger(minutes=5),
        id='indexing_worker',
        max_instances=1,
        next_run_time=now + timedelta(minutes=1)
    )

    # Worker 3: Process deletions every 5 minutes
    scheduler.add_job(
        process_deletions,
        IntervalTrigger(minutes=3),
        id='delete_worker',
        max_instances=1,
        next_run_time=now + timedelta(minutes=2)
    )

    # Worker 4: Weekly S3 reconciliation - Sundays at 2 AM Moscow time
    scheduler.add_job(
        weekly_sync,
        CronTrigger(
            day_of_week='sun',
            hour=2,
            minute=0,
            timezone='Europe/Moscow'
        ),
        id='weekly_sync_worker',
        max_instances=1
    )

    scheduler.start()
    logger.info("APScheduler started with 3 workers")

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
