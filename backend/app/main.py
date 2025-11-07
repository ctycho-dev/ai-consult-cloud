from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.database.connection import db_manager
from app.api.routers import api_router
from app.core.config import settings
from app.core.logger import (
    get_logger,
    cleanup_logger
)
# from app.infrastructure.redis.redis_client import redis_client
from app.middleware.rate_limiter import (
    limiter,
    rate_limit_exceeded_handler
)


logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifecycle."""
    try:
        logger.info("Application startup complete.")
        db_manager.init_engine()
        yield

    except Exception as e:
        logger.error("lifespan: %s", e)
        raise
    finally:
        await db_manager.close()
        cleanup_logger()

app = FastAPI(lifespan=lifespan)

# app.state.limiter = limiter
# app.add_exception_handler(
#     RateLimitExceeded,
#     rate_limit_exceeded_handler
# )

origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(SlowAPIMiddleware)

# Include API routers
app.include_router(api_router, prefix=settings.API_VERSION)

logger.info('Start application')


# @limiter.limit("5/minute")
@app.get("/health")
async def health_check(request: Request):
    return {"status": "healthy"}
