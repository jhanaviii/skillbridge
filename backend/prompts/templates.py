"""Prompt templates for Anthropic Claude API calls.

Each function returns a fully-formed (system_prompt, user_prompt) tuple.
Plain f-strings — no template engines, no dependencies.
"""

from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT = (
    "You are SkillBridge, a career analysis engine. You help professionals "
    "identify skill gaps and build actionable learning roadmaps.\n\n"
    "You MUST respond with valid JSON only — no markdown fences, no preamble, "
    "no explanation outside the JSON structure. Your response must parse as a "
    "single JSON object."
)


def build_analysis_prompt(
    profile: dict[str, Any],
    job: dict[str, Any],
    matched_skills: list[str],
    missing_skills: list[str],
    match_percentage: float,
) -> str:
    """Build the user-turn prompt for combined gap analysis + roadmap.

    The deterministic baseline (matched/missing/percentage) is pre-computed
    by the fallback engine and injected here as ground truth. The AI's job
    is *enhancement* — priority reasoning, semantic matching, narrative —
    not computation.
    """
    profile_json = json.dumps(profile, indent=2, default=str)
    job_json = json.dumps(job, indent=2, default=str)

    return f"""## TASK
Analyze the skill gap between the candidate profile and target job description below.
Then generate a personalized career roadmap to close the gaps.

## CANDIDATE PROFILE
{profile_json}

## TARGET JOB DESCRIPTION
{job_json}

## DETERMINISTIC BASELINE (pre-computed, use as ground truth)
- Matched skills: {json.dumps(matched_skills)}
- Missing skills: {json.dumps(missing_skills)}
- Match percentage: {match_percentage:.1f}%

## INSTRUCTIONS

### Part 1: Enhanced Gap Analysis
For each missing skill in the baseline, provide:
1. priority: "critical" | "important" | "nice_to_have"
   - "critical" = appears in required_skills AND is foundational for the role
   - "important" = appears in required_skills but is learnable quickly
   - "nice_to_have" = appears only in nice_to_have list
2. reason: One sentence explaining WHY this priority level (reference the job context)
3. semantic_match_found: Check if the candidate has an EQUIVALENT skill under a different name
   (e.g., "React.js" ≈ "React", "AWS" ≈ "Amazon Web Services", "CI/CD" ≈ "Jenkins pipelines")
   If found, set to true and explain in the reason.

Assess seniority_fit:
- Compare candidate years_experience against job min_years/max_years
- "good_fit" = within range, "stretch" = 1-2 years below min, "significant_gap" = 3+ years below

### Part 2: Career Roadmap
1. recommended_courses: For each missing skill (after semantic matching), suggest ONE course:
   - Prefer free resources (freeCodeCamp, official docs, MIT OCW) over paid
   - Include realistic estimated_hours (not marketing hours)
   - Include a reason tying the course back to the specific gap
2. milestones: Create 3-5 checkpoints spaced across the learning timeline
   - Each milestone should unlock a testable capability
   - Example: "Week 4: Deploy a containerized app to a local Kubernetes cluster"
3. estimated_weeks_to_ready: Total weeks assuming 10-15 hours/week of study
4. ai_narrative: 3-5 paragraphs of personalized career advice:
   - Acknowledge what the candidate already brings (strengths framing)
   - Be specific about the gap-closing strategy
   - If seniority_fit is "stretch" or "significant_gap", suggest intermediate roles
   - Tone: encouraging, direct, specific
5. confidence_note: Your self-assessed confidence in this analysis:
   - "high" if the role is well-defined and skills are standard
   - "medium" if some skills are ambiguous or the role is niche
   - "low" if the job description is vague or skills don't map cleanly

<fallback_instruction>
If you are uncertain about a skill's priority or cannot find a suitable course:
- Default priority to "important" (not critical) — err toward not over-alarming the user
- For courses, recommend the official documentation of the technology as the course
  (e.g., "Kubernetes Official Docs" at kubernetes.io/docs)
- Set confidence_note to "medium" or "low" and explain what you're unsure about
- NEVER fabricate course names, URLs, or provider names. If unsure, use:
  {{"course_name": "Official Documentation", "provider": "Project Website", "url": "N/A", "estimated_hours": 20}}
Do NOT hallucinate. Uncertainty is acceptable. Fabrication is not.
</fallback_instruction>

## REQUIRED OUTPUT FORMAT
{{
  "enhanced_gap": {{
    "priority_order": [
      {{"skill": "string", "priority": "critical|important|nice_to_have", "reason": "string", "semantic_match_found": false}}
    ],
    "seniority_fit": "good_fit|stretch|significant_gap",
    "semantic_corrections": [
      {{"user_skill": "string", "equivalent_to": "string", "moved_to_matched": true}}
    ]
  }},
  "roadmap": {{
    "recommended_courses": [
      {{"skill": "string", "course_name": "string", "provider": "string", "url": "string", "estimated_hours": 0, "cost": "free|paid", "reason": "string"}}
    ],
    "milestones": [
      {{"week": 0, "checkpoint": "string", "skills_unlocked": ["string"]}}
    ],
    "estimated_weeks_to_ready": 0,
    "ai_narrative": "string",
    "confidence_note": "string"
  }}
}}"""
