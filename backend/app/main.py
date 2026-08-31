from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="F1 Lightning McQueen API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)
# The replay endpoint is the first response in this API large enough for
# compression to matter (tens of thousands of telemetry frames as JSON).
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(health_router)
app.include_router(v1_router, prefix="/api/v1")
