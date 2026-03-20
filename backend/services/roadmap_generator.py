"""Career roadmap generator.

Builds a personalized learning plan from a SkillGapResult.
AI generates narrative + course recommendations; fallback uses the
static taxonomy and template text.
"""

from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone

from backend.models import (
    CareerRoadmap,
    Milestone,
    RecommendedCourse,
    SkillGapResult,
    SkillPriority,
)
from backend.prompts.templates import SYSTEM_PROMPT, build_analysis_prompt
from backend.services.ai_client import AIServiceError, call_anthropic
from backend.services.fallback import rule_based_analyze
from backend import data_loader

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else 3
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _build_fallback_roadmap(
    profile: dict,
    job: dict,
    gap_result: SkillGapResult,
) -> CareerRoadmap:
    """Generate a roadmap using only the static taxonomy — no AI needed."""

    courses: list[RecommendedCourse] = []
    for ps in gap_result.priority_order:
        entry = data_loader.get_fallback_course(ps.skill)
        if entry:
            courses.append(
                RecommendedCourse(
                    skill=ps.skill,
                    course_name=entry["course_name"],
                    provider=entry["provider"],
                    url=entry["url"],
                    estimated_hours=entry["estimated_hours"],
                    cost=entry["cost"],
                    reason=f"Covers the {ps.priority.value} skill gap in {ps.skill}",
                )
            )
        else:
            courses.append(
                RecommendedCourse(
                    skill=ps.skill,
                    course_name="Official Documentation",
                    provider="Project Website",
                    url="N/A — search for latest",
                    estimated_hours=20,
                    cost="free",
                    reason=f"No specific course found; official docs are the best starting point for {ps.skill}",
                )
            )

    # Estimate weeks: critical×4 + important×2 + nice×1
    critical_count = sum(1 for p in gap_result.priority_order if p.priority == SkillPriority.CRITICAL)
    important_count = sum(1 for p in gap_result.priority_order if p.priority == SkillPriority.IMPORTANT)
    nice_count = sum(1 for p in gap_result.priority_order if p.priority == SkillPriority.NICE_TO_HAVE)
    estimated_weeks = (critical_count * 4) + (important_count * 2) + (nice_count * 1)
    estimated_weeks = max(estimated_weeks, 1)

    # Build evenly-spaced milestones
    milestones: list[Milestone] = []
    skills_per_milestone = max(1, math.ceil(len(gap_result.missing_skills) / 3))
    for i in range(0, len(gap_result.missing_skills), skills_per_milestone):
        chunk = gap_result.missing_skills[i : i + skills_per_milestone]
        week = int((i / max(len(gap_result.missing_skills), 1)) * estimated_weeks) + 2
        milestones.append(
            Milestone(
                week=week,
                checkpoint=f"Complete foundational learning for: {', '.join(chunk)}",
                skills_unlocked=chunk,
            )
        )

    # Template narrative
    name = profile.get("name", "Candidate")
    job_title = job.get("title", "target role")
    pct = gap_result.match_percentage

    narrative = (
        f"{name}, you currently match {pct:.0f}% of the required skills for the "
        f"{job_title} position. "
    )
    if gap_result.matched_skills:
        narrative += (
            f"Your existing strengths in {', '.join(gap_result.matched_skills[:4])} "
            f"provide a solid foundation to build upon. "
        )
    if gap_result.missing_skills:
        narrative += (
            f"\n\nTo close the gap, focus on these missing skills in priority order: "
            f"{', '.join(gap_result.missing_skills[:5])}. "
            f"The recommended courses below are organized to help you build each "
            f"skill systematically over approximately {estimated_weeks} weeks."
        )
    if gap_result.seniority_fit in ("stretch", "significant_gap"):
        narrative += (
            f"\n\nNote: This role expects more experience than you currently have "
            f"(seniority fit: {gap_result.seniority_fit}). Consider applying to "
            f"junior-level positions in the same domain to build experience while "
            f"completing this learning plan."
        )
    narrative += (
        "\n\n(This roadmap was generated using rule-based analysis because the AI "
        "service was unavailable. Re-run the analysis when the service is back for "
        "more personalized recommendations.)"
    )

    return CareerRoadmap(
        profile_id=gap_result.profile_id,
        job_id=gap_result.job_id,
        gap_result=gap_result,
        recommended_courses=courses,
        milestones=milestones,
        estimated_weeks_to_ready=estimated_weeks,
        ai_narrative=narrative,
        fallback_used=True,
        generated_at=datetime.now(timezone.utc),
        confidence_note="medium — generated by rule-based fallback, not AI",
    )


async def generate(
    profile: dict,
    job: dict,
    gap_result: SkillGapResult,
) -> CareerRoadmap:
    """Generate a career roadmap: AI-powered with fallback.

    Args:
        profile: Raw profile dict.
        job: Raw job dict.
        gap_result: Pre-computed SkillGapResult from the gap analyzer.

    Returns:
        CareerRoadmap — always populated regardless of AI availability.
    """
    # Try AI-powered roadmap
    try:
        user_prompt = build_analysis_prompt(
            profile=profile,
            job=job,
            matched_skills=gap_result.matched_skills,
            missing_skills=gap_result.missing_skills,
            match_percentage=gap_result.match_percentage,
        )

        raw_response = await call_anthropic(
            user_prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
        )

        cleaned = _strip_json_fences(raw_response)
        ai_data = json.loads(cleaned)
        roadmap_data = ai_data.get("roadmap", {})

        # Parse courses
        courses: list[RecommendedCourse] = []
        for c in roadmap_data.get("recommended_courses", []):
            try:
                courses.append(
                    RecommendedCourse(
                        skill=c["skill"],
                        course_name=c["course_name"],
                        provider=c["provider"],
                        url=c.get("url", "N/A"),
                        estimated_hours=c.get("estimated_hours", 20),
                        cost=c.get("cost", "free"),
                        reason=c.get("reason", "AI-recommended"),
                    )
                )
            except (KeyError, TypeError) as e:
                logger.warning("Skipping malformed course recommendation: %s", e)

        # Parse milestones
        milestones: list[Milestone] = []
        for m in roadmap_data.get("milestones", []):
            try:
                milestones.append(
                    Milestone(
                        week=m["week"],
                        checkpoint=m["checkpoint"],
                        skills_unlocked=m.get("skills_unlocked", []),
                    )
                )
            except (KeyError, TypeError) as e:
                logger.warning("Skipping malformed milestone: %s", e)

        result = CareerRoadmap(
            profile_id=gap_result.profile_id,
            job_id=gap_result.job_id,
            gap_result=gap_result,
            recommended_courses=courses,
            milestones=milestones,
            estimated_weeks_to_ready=roadmap_data.get("estimated_weeks_to_ready", 8),
            ai_narrative=roadmap_data.get("ai_narrative", "AI narrative unavailable."),
            fallback_used=False,
            generated_at=datetime.now(timezone.utc),
            confidence_note=roadmap_data.get("confidence_note", "medium"),
        )

        logger.info(
            "AI roadmap generated | courses=%d | milestones=%d | weeks=%d",
            len(courses),
            len(milestones),
            result.estimated_weeks_to_ready,
        )
        return result

    except AIServiceError as e:
        logger.warning("AI unavailable for roadmap, using fallback: %s", e)
        return _build_fallback_roadmap(profile, job, gap_result)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse AI roadmap response, using fallback: %s", e)
        return _build_fallback_roadmap(profile, job, gap_result)

    except Exception as e:
        logger.error("Unexpected error in roadmap generation, using fallback: %s", e)
        return _build_fallback_roadmap(profile, job, gap_result)
