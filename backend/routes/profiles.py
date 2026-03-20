"""Profile management endpoints — CRUD operations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.models import ProfileCreateRequest, ProfileUpdateRequest, UserProfile
from backend import data_loader

router = APIRouter(tags=["Profiles"])


@router.post(
    "/profiles",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user profile",
    description="Create a new candidate profile. Skills are normalized to lowercase and deduplicated.",
)
async def create_profile(body: ProfileCreateRequest) -> UserProfile:
    profile = UserProfile(
        name=body.name,
        email=body.email,
        current_skills=body.current_skills,
        years_experience=body.years_experience,
        education=body.education,
        target_role=body.target_role,
        background_summary=body.background_summary,
    )
    data_loader.save_profile(profile.model_dump(mode="json"))
    return profile


@router.get(
    "/profiles",
    response_model=list[dict],
    summary="List all profiles (pre-seeded + user-created)",
)
async def list_profiles():
    return list(data_loader._profiles_store.values())


@router.get(
    "/profiles/{profile_id}",
    response_model=dict,
    summary="Get a single profile by ID",
)
async def get_profile(profile_id: str):
    profile = data_loader.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    return profile


@router.patch(
    "/profiles/{profile_id}",
    response_model=dict,
    summary="Partially update a profile",
    description=(
        "Update specific fields of an existing profile. Only provided fields are changed. "
        "Skills are re-normalized if updated. Returns the full updated profile."
    ),
)
async def update_profile(profile_id: str, body: ProfileUpdateRequest):
    profile = data_loader.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        profile[key] = value

    data_loader.save_profile(profile)
    return profile
