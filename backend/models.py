"""Pydantic v2 domain models for SkillBridge Career Navigator.

Every model includes json_schema_extra so FastAPI's /docs shows realistic
example payloads — critical because Swagger UI *is* the demo interface.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Seniority(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class SkillPriority(str, Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    NICE_TO_HAVE = "nice_to_have"


class AIServiceStatus(str, Enum):
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _normalize_skill_list(v: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for s in v:
        normed = s.strip().lower()
        if normed and normed not in seen:
            seen.add(normed)
            out.append(normed)
    if not out:
        raise ValueError("At least one non-empty skill is required")
    return out


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    current_skills: list[str] = Field(..., min_length=1)
    years_experience: float = Field(..., ge=0, le=50)
    education: str = Field(..., max_length=300)
    target_role: str = Field(..., min_length=1)
    background_summary: str = Field(..., max_length=2000)

    @field_validator("current_skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        return _normalize_skill_list(v)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "Priya Venkatesh",
                "email": "priya.v@example.com",
                "current_skills": ["python", "java", "sql", "git", "data structures"],
                "years_experience": 0,
                "education": "B.Tech Computer Science, Manipal Institute of Technology",
                "target_role": "Cloud Engineer",
                "background_summary": "Fresh CS graduate with a published paper on distributed caching.",
            }]
        }
    }


class ProfileUpdateRequest(BaseModel):
    """Partial profile update — only provided fields are changed."""
    current_skills: Optional[list[str]] = Field(None)
    years_experience: Optional[float] = Field(None, ge=0, le=50)
    target_role: Optional[str] = Field(None, min_length=1)
    background_summary: Optional[str] = Field(None, max_length=2000)

    @field_validator("current_skills", mode="before")
    @classmethod
    def normalize_skills(cls, v):
        if v is None:
            return None
        return _normalize_skill_list(v)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "current_skills": ["python", "docker", "linux", "kubernetes"],
                "years_experience": 2.5,
            }]
        }
    }


class AnalyzeRequest(BaseModel):
    profile_id: str
    job_id: str
    model_config = {"json_schema_extra": {"examples": [{"profile_id": "a1b2c3d4-1111-4000-8000-000000000001", "job_id": "job-cloud-junior-01"}]}}


class RoadmapRequest(BaseModel):
    profile_id: str
    job_id: str
    model_config = {"json_schema_extra": {"examples": [{"profile_id": "a1b2c3d4-2222-4000-8000-000000000002", "job_id": "job-frontend-mid-01"}]}}


class InterviewPrepRequest(BaseModel):
    profile_id: str
    job_id: str
    model_config = {"json_schema_extra": {"examples": [{"profile_id": "a1b2c3d4-2222-4000-8000-000000000002", "job_id": "job-frontend-mid-01"}]}}


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    current_skills: list[str]
    years_experience: float = Field(ge=0, le=50)
    education: str
    target_role: str
    background_summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobDescription(BaseModel):
    id: str
    title: str
    role_category: str
    seniority: Seniority
    required_skills: list[str]
    nice_to_have: list[str] = []
    description: str
    company_type: str
    min_years: int = Field(ge=0)
    max_years: int = Field(ge=0)


class PrioritizedSkill(BaseModel):
    skill: str
    priority: SkillPriority
    reason: str
    semantic_match_found: bool = False


class SkillGapResult(BaseModel):
    profile_id: str
    job_id: str
    matched_skills: list[str]
    missing_skills: list[str]
    priority_order: list[PrioritizedSkill]
    match_percentage: float = Field(ge=0, le=100)
    seniority_fit: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fallback_used: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "profile_id": "a1b2c3d4-2222-4000-8000-000000000002",
                "job_id": "job-frontend-mid-01",
                "matched_skills": ["javascript", "react", "html", "css", "rest apis", "git"],
                "missing_skills": ["typescript", "unit testing", "performance optimization"],
                "priority_order": [
                    {"skill": "typescript", "priority": "critical", "reason": "Required for type-safe frontend development", "semantic_match_found": False},
                ],
                "match_percentage": 66.7,
                "seniority_fit": "good_fit",
                "analyzed_at": "2025-03-19T10:30:00Z",
                "fallback_used": False,
            }]
        }
    }


class RecommendedCourse(BaseModel):
    skill: str
    course_name: str
    provider: str
    url: str
    estimated_hours: int
    cost: str
    reason: str


class Milestone(BaseModel):
    week: int
    checkpoint: str
    skills_unlocked: list[str]


class CareerRoadmap(BaseModel):
    profile_id: str
    job_id: str
    gap_result: SkillGapResult
    recommended_courses: list[RecommendedCourse]
    milestones: list[Milestone]
    estimated_weeks_to_ready: int = Field(ge=0)
    ai_narrative: str
    fallback_used: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_note: str = Field(default="medium")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "profile_id": "a1b2c3d4-2222-4000-8000-000000000002",
                "job_id": "job-frontend-mid-01",
                "gap_result": SkillGapResult.model_config["json_schema_extra"]["examples"][0],
                "recommended_courses": [{"skill": "typescript", "course_name": "TypeScript for Pros", "provider": "Udemy", "url": "https://udemy.com", "estimated_hours": 25, "cost": "paid", "reason": "Closes critical gap"}],
                "milestones": [{"week": 3, "checkpoint": "Complete TS fundamentals", "skills_unlocked": ["typescript"]}],
                "estimated_weeks_to_ready": 8,
                "ai_narrative": "You already have a strong frontend foundation...",
                "fallback_used": False,
                "generated_at": "2025-03-19T10:31:00Z",
                "confidence_note": "high",
            }]
        }
    }


class InterviewQuestion(BaseModel):
    skill: str
    question: str
    difficulty: str = Field(description="easy | medium | hard")
    what_to_look_for: str


class InterviewPrepResponse(BaseModel):
    profile_id: str
    job_id: str
    questions: list[InterviewQuestion]
    fallback_used: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "profile_id": "a1b2c3d4-2222-4000-8000-000000000002",
                "job_id": "job-frontend-mid-01",
                "questions": [{
                    "skill": "typescript",
                    "question": "Walk me through how you would define a generic API response wrapper that handles both success and error states using TypeScript.",
                    "difficulty": "hard",
                    "what_to_look_for": "Understanding of generic type parameters, union types, and practical API design patterns.",
                }],
                "fallback_used": False,
                "generated_at": "2025-03-19T10:32:00Z",
            }]
        }
    }


class HealthResponse(BaseModel):
    status: AIServiceStatus
    latency_ms: Optional[int] = None
    last_checked: datetime
    ai_configured: bool
