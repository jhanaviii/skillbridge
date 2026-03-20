"""SkillBridge Career Navigator — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend import data_loader
from backend.routes import profiles, jobs, analysis, health

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load synthetic data into memory on startup."""
    logger.info("Loading synthetic data files...")
    data_loader.load_all()
    logger.info(
        "SkillBridge API ready | env=%s | ai_configured=%s",
        settings.APP_ENV,
        settings.ai_configured,
    )
    yield
    logger.info("Shutting down SkillBridge API")


app = FastAPI(
    title=settings.APP_TITLE,
    description=(
        "AI-powered career navigation platform that analyzes skill gaps between "
        "candidate profiles and job descriptions, then generates personalized "
        "learning roadmaps with course recommendations and milestones.\n\n"
        "**Quick start:** All 6 profiles and 12 jobs are pre-loaded. Use the "
        "endpoints below to explore.\n\n"
        "**Demo combos to try:**\n"
        "- Marcus (bootcamp grad) → Mid Frontend Dev: `profile=a1b2c3d4-2222-...0002` + `job=job-frontend-mid-01`\n"
        "- Sarah (career switcher) → Junior Security: `profile=a1b2c3d4-3333-...0003` + `job=job-security-junior-01`\n"
        "- Priya (fresh grad) → Junior Cloud: `profile=a1b2c3d4-1111-...0001` + `job=job-cloud-junior-01`"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route modules under /api prefix
app.include_router(profiles.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(health.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """API root — redirects to /docs for the interactive Swagger UI."""
    return {
        "message": "SkillBridge Career Navigator API",
        "docs": "/docs",
        "health": "/api/health",
    }
