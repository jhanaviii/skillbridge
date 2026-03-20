"""Async client for the Anthropic Messages API.

Thin httpx wrapper — no LangChain, no SDK. Every failure is a standard
HTTP issue with a status code you can debug in seconds.
"""

from __future__ import annotations

import logging
import time

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AIServiceError(Exception):
    """Raised when the Anthropic API call fails for any reason."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


async def call_anthropic(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int | None = None,
    timeout: int | None = None,
) -> str:
    """Send a single-turn message to Claude and return the text response.

    Raises AIServiceError on any failure (network, auth, rate limit, timeout, parse).
    """
    if not settings.ai_configured:
        raise AIServiceError("ANTHROPIC_API_KEY is not configured", status_code=None)

    payload = {
        "model": settings.AI_MODEL,
        "max_tokens": max_tokens or settings.AI_MAX_TOKENS,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    effective_timeout = timeout or settings.AI_TIMEOUT

    logger.info(
        "Calling Anthropic API | model=%s | prompt_len=%d | timeout=%ds",
        settings.AI_MODEL,
        len(user_prompt),
        effective_timeout,
    )

    start = time.monotonic()

    try:
        async with httpx.AsyncClient(timeout=effective_timeout) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                json=payload,
                headers=headers,
            )
    except httpx.TimeoutException:
        elapsed = time.monotonic() - start
        logger.warning("Anthropic API timeout after %.1fs", elapsed)
        raise AIServiceError(f"Request timed out after {effective_timeout}s", status_code=None)
    except httpx.HTTPError as exc:
        elapsed = time.monotonic() - start
        logger.error("Anthropic API HTTP error after %.1fs: %s", elapsed, exc)
        raise AIServiceError(f"HTTP error: {exc}", status_code=None)

    elapsed = time.monotonic() - start

    if response.status_code != 200:
        logger.error(
            "Anthropic API error | status=%d | elapsed=%.1fs | body=%s",
            response.status_code,
            elapsed,
            response.text[:500],
        )
        raise AIServiceError(
            f"API returned {response.status_code}: {response.text[:200]}",
            status_code=response.status_code,
        )

    data = response.json()
    content_blocks = data.get("content", [])
    text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]

    if not text_parts:
        raise AIServiceError("No text content in API response", status_code=200)

    result = "\n".join(text_parts)
    logger.info(
        "Anthropic API success | elapsed=%.1fs | response_len=%d",
        elapsed,
        len(result),
    )
    return result


async def ping_anthropic() -> tuple[bool, int]:
    """Lightweight health check — returns (is_reachable, latency_ms).

    Sends the cheapest possible prompt to verify connectivity.
    """
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                json={
                    "model": settings.AI_MODEL,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Respond with: ok"}],
                },
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
            )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return response.status_code == 200, elapsed_ms
    except Exception:
        return False, 0
