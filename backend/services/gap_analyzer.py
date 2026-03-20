"""Skill gap analysis orchestrator.

Pattern: compute deterministic baseline FIRST, then try AI enhancement,
fall back to baseline on ANY failure. The AI makes the result *better*,
not *possible*.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from backend.models import (
    PrioritizedSkill,
    SkillGapResult,
    SkillPriority,
)
from backend.prompts.templates import SYSTEM_PROMPT, build_analysis_prompt
from backend.services.ai_client import AIServiceError, call_anthropic
from backend.services.fallback import rule_based_analyze

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    """Remove markdown ```json ... ``` fences if present."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else 3
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


async def analyze(profile: dict, job: dict) -> SkillGapResult:
    """Run full gap analysis: deterministic baseline → AI enhancement → fallback.

    Args:
        profile: Raw profile dict (from data_loader or user-created).
        job: Raw job dict (serialized JobDescription).

    Returns:
        SkillGapResult — always populated, regardless of AI availability.
    """
    # -----------------------------------------------------------------------
    # Step 1: ALWAYS compute deterministic baseline
    # -----------------------------------------------------------------------
    baseline = rule_based_analyze(profile, job)
    logger.info(
        "Baseline computed | profile=%s | job=%s | match=%.1f%% | missing=%d",
        profile.get("id"),
        job.get("id"),
        baseline.match_percentage,
        len(baseline.missing_skills),
    )

    # -----------------------------------------------------------------------
    # Step 2: Try AI enhancement
    # -----------------------------------------------------------------------
    try:
        user_prompt = build_analysis_prompt(
            profile=profile,
            job=job,
            matched_skills=baseline.matched_skills,
            missing_skills=baseline.missing_skills,
            match_percentage=baseline.match_percentage,
        )

        raw_response = await call_anthropic(
            user_prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
        )

        # Step 3: Parse AI response and merge with baseline
        cleaned = _strip_json_fences(raw_response)
        ai_data = json.loads(cleaned)
        enhanced_gap = ai_data.get("enhanced_gap", {})

        # Build enhanced priority order from AI response
        ai_priorities: list[PrioritizedSkill] = []
        for item in enhanced_gap.get("priority_order", []):
            try:
                ai_priorities.append(
                    PrioritizedSkill(
                        skill=item["skill"],
                        priority=SkillPriority(item["priority"]),
                        reason=item.get("reason", "AI-assessed priority"),
                        semantic_match_found=item.get("semantic_match_found", False),
                    )
                )
            except (KeyError, ValueError) as e:
                logger.warning("Skipping malformed AI priority item: %s — %s", item, e)

        # Handle semantic corrections: move skills from missing to matched
        semantic_corrections = enhanced_gap.get("semantic_corrections", [])
        extra_matched: list[str] = []
        for corr in semantic_corrections:
            if corr.get("moved_to_matched"):
                extra_matched.append(corr.get("equivalent_to", ""))

        final_matched = sorted(set(baseline.matched_skills) | set(extra_matched))
        final_missing = sorted(set(baseline.missing_skills) - set(extra_matched))

        # Recalculate match percentage if semantic corrections changed things
        required_set = {s.lower() for s in job.get("required_skills", [])}
        matched_required = {s for s in final_matched if s in required_set}
        pct = (len(matched_required) / len(required_set) * 100) if required_set else 100.0

        result = SkillGapResult(
            profile_id=profile.get("id", "unknown"),
            job_id=job.get("id", "unknown"),
            matched_skills=final_matched,
            missing_skills=final_missing,
            priority_order=ai_priorities if ai_priorities else baseline.priority_order,
            match_percentage=round(pct, 1),
            seniority_fit=enhanced_gap.get("seniority_fit", baseline.seniority_fit),
            analyzed_at=datetime.now(timezone.utc),
            fallback_used=False,
        )

        logger.info(
            "AI-enhanced analysis complete | semantic_corrections=%d | match=%.1f%%",
            len(semantic_corrections),
            result.match_percentage,
        )
        return result

    except AIServiceError as e:
        logger.warning("AI service unavailable, using fallback: %s", e)
        return baseline

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse AI response, using fallback: %s", e)
        return baseline

    except Exception as e:
        logger.error("Unexpected error in AI enhancement, using fallback: %s", e)
        return baseline
