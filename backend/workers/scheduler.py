import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from workers.upload_worker import process_upload_batch
from workers.indexing_worker import check_indexing_status
from workers.upload_worker import process_upload_batch
from workers.delete_worker import process_deletions
from app.core.logger import get_logger

logger = get_logger('app.scheduler')


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler()

    # Worker 1: Upload to OpenAI every 2 minutes
    # scheduler.add_job(
    #     process_upload_batch,
    #     IntervalTrigger(minutes=3),
    #     id='upload_worker',
    #     max_instances=1
    # )

    # Worker 2: Check indexing status every 2 minutes
    # scheduler.add_job(
    #     check_indexing_status,
    #     IntervalTrigger(minutes=5),
    #     id='indexing_worker',
    #     max_instances=1
    # )

    # Worker 3: Process deletions every 5 minutes
    scheduler.add_job(
        process_deletions,
        IntervalTrigger(minutes=3),
        id='delete_worker',
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
