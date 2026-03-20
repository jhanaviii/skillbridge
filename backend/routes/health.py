"""AI service health check endpoint with TTL caching."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter

from backend.config import settings
from backend.models import AIServiceStatus, HealthResponse
from backend.services.ai_client import ping_anthropic

router = APIRouter(tags=["Health"])

# Simple in-memory cache to avoid hammering the API on every poll
_cache: dict = {"response": None, "expires_at": 0.0}


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check AI service health",
    description=(
        "Pings the Anthropic API with a minimal prompt and returns status "
        "(up/degraded/down) with round-trip latency in milliseconds. "
        "Result is cached for 60 seconds to avoid excessive API calls. "
        "The frontend HealthBadge component polls this every 30 seconds."
    ),
)
async def health_check() -> HealthResponse:
    now = time.monotonic()

    # Return cached response if still fresh
    if _cache["response"] and now < _cache["expires_at"]:
        return _cache["response"]

    # If API key isn't configured, report DOWN immediately
    if not settings.ai_configured:
        resp = HealthResponse(
            status=AIServiceStatus.DOWN,
            latency_ms=None,
            last_checked=datetime.now(timezone.utc),
            ai_configured=False,
        )
        _cache["response"] = resp
        _cache["expires_at"] = now + settings.HEALTH_CHECK_CACHE_TTL
        return resp

    # Ping Anthropic
    reachable, latency_ms = await ping_anthropic()

    if not reachable:
        status_val = AIServiceStatus.DOWN
    elif latency_ms > 3000:
        status_val = AIServiceStatus.DEGRADED
    else:
        status_val = AIServiceStatus.UP

    resp = HealthResponse(
        status=status_val,
        latency_ms=latency_ms if reachable else None,
        last_checked=datetime.now(timezone.utc),
        ai_configured=True,
    )
    _cache["response"] = resp
    _cache["expires_at"] = now + settings.HEALTH_CHECK_CACHE_TTL
    return resp
