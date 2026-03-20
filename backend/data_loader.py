"""Load synthetic data files into memory at application startup.

All data lives in-memory as plain Python structures. This is intentional —
the case study requires no database, and in-memory access keeps the demo
snappy while making the code easy to follow.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from backend.config import settings
from backend.models import JobDescription

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory stores (populated by load_all())
# ---------------------------------------------------------------------------

_profiles_store: dict[str, dict] = {}  # id -> raw profile dict
_jobs: list[JobDescription] = []
_courses: list[dict] = []
_fallback_taxonomy: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Startup loader
# ---------------------------------------------------------------------------

def load_all() -> None:
    """Read every JSON file from data/ into memory. Call once at startup."""
    global _jobs, _courses, _fallback_taxonomy

    data_dir: Path = settings.DATA_DIR

    # --- Profiles (pre-seed from synthetic file) ---
    profiles_path = data_dir / "resumes.json"
    if profiles_path.exists():
        raw = json.loads(profiles_path.read_text())
        for p in raw:
            _profiles_store[p["id"]] = p
        logger.info("Loaded %d seed profiles from resumes.json", len(_profiles_store))

    # --- Jobs ---
    jobs_path = data_dir / "jobs.json"
    raw_jobs = json.loads(jobs_path.read_text())
    _jobs = [JobDescription(**j) for j in raw_jobs]
    logger.info("Loaded %d job descriptions from jobs.json", len(_jobs))

    # --- Courses ---
    courses_path = data_dir / "courses.json"
    _courses = json.loads(courses_path.read_text())
    logger.info("Loaded %d courses from courses.json", len(_courses))

    # --- Fallback taxonomy ---
    taxonomy_path = data_dir / "fallback_skill_taxonomy.json"
    _fallback_taxonomy = json.loads(taxonomy_path.read_text())
    logger.info(
        "Loaded fallback taxonomy with %d skill entries", len(_fallback_taxonomy)
    )


# ---------------------------------------------------------------------------
# Profile CRUD (in-memory)
# ---------------------------------------------------------------------------

def save_profile(profile_dict: dict) -> None:
    """Store a profile dict keyed by its id."""
    _profiles_store[profile_dict["id"]] = profile_dict


def get_profile_by_id(profile_id: str) -> Optional[dict]:
    """Return a profile dict or None."""
    return _profiles_store.get(profile_id)


# ---------------------------------------------------------------------------
# Job accessors
# ---------------------------------------------------------------------------

def get_all_jobs() -> list[JobDescription]:
    return list(_jobs)


def get_job_by_id(job_id: str) -> Optional[JobDescription]:
    for j in _jobs:
        if j.id == job_id:
            return j
    return None


def filter_jobs(
    role: Optional[str] = None,
    seniority: Optional[str] = None,
    search: Optional[str] = None,
) -> list[JobDescription]:
    """Filter jobs by role substring, exact seniority, or free-text search."""
    results = list(_jobs)

    if role:
        q = role.lower()
        results = [j for j in results if q in j.role_category.lower() or q in j.title.lower()]

    if seniority:
        results = [j for j in results if j.seniority.value == seniority.lower()]

    if search:
        q = search.lower()
        results = [
            j for j in results
            if q in j.title.lower()
            or q in j.description.lower()
            or any(q in s for s in j.required_skills)
        ]

    return results


# ---------------------------------------------------------------------------
# Course / taxonomy accessors
# ---------------------------------------------------------------------------

def get_courses_for_skills(skills: list[str]) -> list[dict]:
    """Return matching courses from courses.json for the given skill names."""
    skill_set = {s.lower() for s in skills}
    return [c for c in _courses if c["skill_covered"].lower() in skill_set]


def get_fallback_taxonomy() -> dict[str, dict]:
    """Return the full skill → course fallback mapping."""
    return dict(_fallback_taxonomy)


def get_fallback_course(skill: str) -> Optional[dict]:
    """Lookup a single skill in the fallback taxonomy."""
    return _fallback_taxonomy.get(skill.lower())
