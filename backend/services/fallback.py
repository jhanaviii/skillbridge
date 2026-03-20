"""Rule-based fallback for skill gap analysis.

Used when the AI service is unavailable or returns unparseable results.
All operations are deterministic set math — no external calls.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.models import (
    PrioritizedSkill,
    SkillGapResult,
    SkillPriority,
)


def _normalize(skills: list[str]) -> set[str]:
    return {s.strip().lower() for s in skills}


def compute_seniority_fit(years_exp: float, min_years: int, max_years: int) -> str:
    """Classify how well candidate experience matches job expectations."""
    if years_exp >= min_years:
        return "good_fit"
    gap = min_years - years_exp
    if gap <= 2:
        return "stretch"
    return "significant_gap"


def rule_based_analyze(profile: dict, job: dict) -> SkillGapResult:
    """Compute a skill gap result using only set operations and static rules.

    This is the *always-available* baseline. The AI enhances it; this replaces it
    when the AI is down.
    """
    user_skills = _normalize(profile.get("current_skills", []))
    required = _normalize(job.get("required_skills", []))
    nice = _normalize(job.get("nice_to_have", []))

    all_job_skills = required | nice

    matched = sorted(user_skills & all_job_skills)
    missing = sorted(all_job_skills - user_skills)

    # Match percentage uses ONLY required skills in the denominator
    matched_required = user_skills & required
    pct = (len(matched_required) / len(required) * 100) if required else 100.0

    # Priority: required skills → "important", nice-to-have → "nice_to_have"
    priority_order: list[PrioritizedSkill] = []
    for skill in sorted(required - user_skills):
        priority_order.append(
            PrioritizedSkill(
                skill=skill,
                priority=SkillPriority.IMPORTANT,
                reason=f"Listed as a required skill for this {job.get('seniority', '')} role",
                semantic_match_found=False,
            )
        )
    for skill in sorted(nice - user_skills):
        priority_order.append(
            PrioritizedSkill(
                skill=skill,
                priority=SkillPriority.NICE_TO_HAVE,
                reason=f"Listed as a nice-to-have skill",
                semantic_match_found=False,
            )
        )

    seniority_fit = compute_seniority_fit(
        profile.get("years_experience", 0),
        job.get("min_years", 0),
        job.get("max_years", 99),
    )

    return SkillGapResult(
        profile_id=profile.get("id", "unknown"),
        job_id=job.get("id", "unknown"),
        matched_skills=matched,
        missing_skills=missing,
        priority_order=priority_order,
        match_percentage=round(pct, 1),
        seniority_fit=seniority_fit,
        analyzed_at=datetime.now(timezone.utc),
        fallback_used=True,
    )
