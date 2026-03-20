"""Skill gap analysis, career roadmap, and interview prep endpoints."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models import (
    AnalyzeRequest,
    CareerRoadmap,
    InterviewPrepRequest,
    InterviewPrepResponse,
    InterviewQuestion,
    RoadmapRequest,
    SkillGapResult,
)
from backend import data_loader
from backend.services import gap_analyzer, roadmap_generator
from backend.services.ai_client import AIServiceError, call_anthropic

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])


def _get_profile_and_job(profile_id: str, job_id: str) -> tuple[dict, dict]:
    profile = data_loader.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found. Use GET /api/profiles to see available profiles.")
    job_obj = data_loader.get_job_by_id(job_id)
    if not job_obj:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found. Use GET /api/jobs to see available jobs.")
    return profile, job_obj.model_dump()


@router.post("/analyze", response_model=SkillGapResult, summary="Analyze skill gap between a profile and a job",
    description="Computes a deterministic skill match baseline, then enhances with AI. Falls back to rule-based on failure.")
async def analyze_gap(body: AnalyzeRequest) -> SkillGapResult:
    profile, job = _get_profile_and_job(body.profile_id, body.job_id)
    return await gap_analyzer.analyze(profile, job)


@router.post("/roadmap", response_model=CareerRoadmap, summary="Generate a personalized career roadmap",
    description="Runs gap analysis internally, then generates courses, milestones, and AI narrative.")
async def generate_roadmap(body: RoadmapRequest) -> CareerRoadmap:
    profile, job = _get_profile_and_job(body.profile_id, body.job_id)
    gap_result = await gap_analyzer.analyze(profile, job)
    return await roadmap_generator.generate(profile, job, gap_result)


# ---------------------------------------------------------------------------
# Interview Prep
# ---------------------------------------------------------------------------

_INTERVIEW_SYSTEM = (
    "You are SkillBridge Interview Coach. You generate targeted technical interview "
    "questions based on a candidate's specific skill gaps for a target role.\n\n"
    "Respond with valid JSON only — no markdown, no preamble."
)


def _build_interview_prompt(profile: dict, job: dict, gap_result: SkillGapResult) -> str:
    """Build the prompt for interview question generation."""
    skills_with_priority = []
    for p in gap_result.priority_order:
        if p.priority.value in ("critical", "important"):
            skills_with_priority.append({"skill": p.skill, "priority": p.priority.value})

    return f"""## TASK
Generate 5-7 technical interview questions targeting this candidate's specific skill gaps for the target job.

## CANDIDATE
Name: {profile.get('name')}
Current skills: {json.dumps(profile.get('current_skills', []))}
Experience: {profile.get('years_experience')} years

## TARGET JOB
Title: {job.get('title')}
Seniority: {job.get('seniority')}
Description: {job.get('description')}

## SKILL GAPS TO TARGET
{json.dumps(skills_with_priority, indent=2)}

## INSTRUCTIONS
- Generate 5-7 questions, one per skill gap (prioritize critical skills)
- Each question must reference the actual job context, not be generic
- For critical skills: difficulty = "hard"
- For important skills: difficulty = "medium"
- For nice_to_have skills: difficulty = "easy"
- what_to_look_for: 1-2 sentences on what a good answer demonstrates

## REQUIRED OUTPUT FORMAT
{{
  "questions": [
    {{
      "skill": "string",
      "question": "string",
      "difficulty": "easy|medium|hard",
      "what_to_look_for": "string"
    }}
  ]
}}"""


def _build_fallback_questions(gap_result: SkillGapResult, job: dict) -> list[InterviewQuestion]:
    """Generate template questions when AI is unavailable."""
    questions: list[InterviewQuestion] = []
    job_title = job.get("title", "this role")

    for ps in gap_result.priority_order:
        if ps.priority.value == "critical":
            diff = "hard"
        elif ps.priority.value == "important":
            diff = "medium"
        else:
            diff = "easy"

        questions.append(InterviewQuestion(
            skill=ps.skill,
            question=f"In the context of a {job_title} position, describe a situation where you would need to use {ps.skill}. What approach would you take and what challenges might you encounter?",
            difficulty=diff,
            what_to_look_for=f"Understanding of {ps.skill} fundamentals, ability to apply it to real scenarios, and awareness of common pitfalls.",
        ))

        if len(questions) >= 7:
            break

    return questions


@router.post(
    "/interview-prep",
    response_model=InterviewPrepResponse,
    summary="Generate interview prep questions targeting skill gaps",
    description=(
        "Runs gap analysis first, then generates 5-7 technical interview questions "
        "targeting the candidate's critical and important skill gaps. Questions are "
        "contextualized to the specific job. Falls back to template questions if AI is unavailable."
    ),
)
async def interview_prep(body: InterviewPrepRequest) -> InterviewPrepResponse:
    profile, job = _get_profile_and_job(body.profile_id, body.job_id)

    # Run gap analysis first
    gap_result = await gap_analyzer.analyze(profile, job)

    # Try AI-generated questions
    try:
        prompt = _build_interview_prompt(profile, job, gap_result)
        raw = await call_anthropic(user_prompt=prompt, system_prompt=_INTERVIEW_SYSTEM)

        # Strip markdown fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[cleaned.index("\n") + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        ai_data = json.loads(cleaned)
        questions = []
        for q in ai_data.get("questions", []):
            try:
                questions.append(InterviewQuestion(
                    skill=q["skill"],
                    question=q["question"],
                    difficulty=q.get("difficulty", "medium"),
                    what_to_look_for=q.get("what_to_look_for", ""),
                ))
            except (KeyError, TypeError):
                continue

        if questions:
            logger.info("AI generated %d interview questions", len(questions))
            return InterviewPrepResponse(
                profile_id=body.profile_id,
                job_id=body.job_id,
                questions=questions,
                fallback_used=False,
            )

        raise ValueError("AI returned no valid questions")

    except Exception as e:
        logger.warning("Interview prep falling back to templates: %s", e)
        return InterviewPrepResponse(
            profile_id=body.profile_id,
            job_id=body.job_id,
            questions=_build_fallback_questions(gap_result, job),
            fallback_used=True,
        )
