import os
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import sys
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.db import init_db
from backend.routes import api_router
from backend.settings import settings

# --- Logging configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("civicnavigator")

# --- Optional Sentry integration ---
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    if getattr(settings, "SENTRY_DSN", None):
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            traces_sample_rate=1.0
        )
        logger.info("Sentry monitoring enabled")
except ImportError:
    logger.warning("Sentry SDK not installed; skipping error tracking setup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only init DB in non-test environments
    if os.getenv("TESTING") != "1":
        init_db()
    yield

app = FastAPI(
    title="CivicNavigator API",
    description="API backend for CivicNavigator MVP: chat, incidents, knowledge base",
    version="0.1.0",
    lifespan=lifespan,
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        response: Response = await call_next(request)
        duration_ms: float = round((time.time() - start_time) * 1000, 2)
        logger.info({
            "method": request.method,
            "path": request.url.path,
            "status_code": int(response.status_code),
            "duration_ms": duration_ms
        })
        return response

app.add_middleware(RequestLoggingMiddleware)

# --- CORS configuration ---
cors_origins = settings.CORS_ORIGINS
logger.info(f"Starting app in {settings.ENV} mode")
logger.info(f"Allowed CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Routes ---
app.include_router(api_router)

@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "version": app.version,
        "env": settings.ENV
    }

# Instrument and expose metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["system"])
