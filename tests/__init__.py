"""Shared test fixtures for SkillBridge Career Navigator.

Fixtures provide a configured test client and reusable mock data
so each test file stays focused on assertions, not setup.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend import data_loader


@pytest.fixture(scope="session", autouse=True)
def _load_data():
    """Load synthetic data files once for the entire test session."""
    data_loader.load_all()


@pytest.fixture()
def client():
    """FastAPI TestClient wrapping the application."""
    return TestClient(app)


@pytest.fixture()
def mock_profile():
    """Ravi Dasgupta — self-taught developer targeting Cloud Engineer.

    Has python, docker, linux (partial match against junior cloud jobs).
    """
    return {
        "name": "Ravi Dasgupta",
        "email": "ravi.d@example.com",
        "current_skills": [
            "python",
            "docker",
            "linux",
            "bash scripting",
            "react",
            "mongodb",
            "git",
        ],
        "years_experience": 2,
        "education": "Self-taught, no formal degree",
        "target_role": "Cloud Engineer",
        "background_summary": "Self-taught developer with two years of freelance and open-source experience.",
    }


@pytest.fixture()
def mock_zero_match_profile():
    """Profile with zero overlapping skills — tests graceful degradation."""
    return {
        "name": "Zero Match Candidate",
        "email": "zero@example.com",
        "current_skills": ["interpretive dance", "watercolor painting"],
        "years_experience": 0,
        "education": "B.A. Fine Arts",
        "target_role": "Cloud Engineer",
        "background_summary": "Artist exploring a career pivot into technology.",
    }


@pytest.fixture()
def junior_cloud_job_id():
    """ID of a pre-loaded junior Cloud Engineer job from synthetic data."""
    return "job-cloud-junior-01"
