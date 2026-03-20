"""Job description listing and filtering endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from backend.models import JobDescription
from backend import data_loader

router = APIRouter(tags=["Jobs"])


@router.get(
    "/jobs",
    response_model=list[JobDescription],
    summary="List and filter job descriptions",
    description=(
        "Returns all 12 synthetic job descriptions. Filter by role category "
        "(substring match on title/role_category), exact seniority level, "
        "or free-text search across title, description, and skills. "
        "All filters are optional and combine with AND logic."
    ),
)
async def list_jobs(
    role: Optional[str] = Query(
        None,
        description="Filter by role category (e.g., 'Cloud Engineer', 'Frontend'). Case-insensitive substring match.",
        examples=["Cloud Engineer", "Frontend", "Security"],
    ),
    seniority: Optional[str] = Query(
        None,
        description="Filter by seniority level. Must be: junior, mid, or senior.",
        examples=["junior", "mid", "senior"],
    ),
    search: Optional[str] = Query(
        None,
        description="Free-text search across title, description, and required skills.",
        examples=["kubernetes", "react", "threat"],
    ),
) -> list[JobDescription]:
    return data_loader.filter_jobs(role=role, seniority=seniority, search=search)


@router.get(
    "/jobs/{job_id}",
    response_model=JobDescription,
    summary="Get a single job description by ID",
)
async def get_job(job_id: str):
    from fastapi import HTTPException
    job = data_loader.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job
