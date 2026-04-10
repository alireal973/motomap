"""MotoMap API application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db, close_db
from api.core.cache import cache
from api.models import *  # noqa: F401,F403 -- ensure all models register with Base.metadata
from api.routes.auth import router as auth_router
from api.routes.profile import router as profile_router
from api.routes.route_preview import router as route_preview_router
from api.routes.weather import router as weather_router
from api.routes.communities import router as communities_router
from api.routes.road_reports import router as road_reports_router
from api.routes.gamification import router as gamification_router
from api.routes.history import router as history_router
from api.routes.notifications import router as notifications_router
from api.routes.upload import router as upload_router
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.logging import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.connect()
    await init_db()
    logger.info("MotoMap API started")
    yield
    await close_db()
    await cache.close()
    logger.info("MotoMap API shut down")


app = FastAPI(
    title="MotoMap API",
    description="Motorcycle-aware routing and community platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(route_preview_router)
app.include_router(weather_router)
app.include_router(communities_router)
app.include_router(road_reports_router)
app.include_router(gamification_router)
app.include_router(history_router)
app.include_router(notifications_router)
app.include_router(upload_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
