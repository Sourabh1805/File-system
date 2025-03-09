import logging
from contextlib import asynccontextmanager
from api.routes.filesystem import router as fs_router
import asgi_correlation_id
from fastapi import FastAPI

from api.logging_config import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Hello World")
    logger.info(logging.getLogger(__name__))
    logger.info(__name__)
    logger.info("Hello World")
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)
app.include_router(fs_router, prefix="/api/v1")
