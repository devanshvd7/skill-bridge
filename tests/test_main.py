"""Tests for the Skill-Bridge Career Navigator API."""

import io
from unittest.mock import patch

import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------------------------
# Helpers: create minimal PDFs in memory so tests are fully self-contained
# ---------------------------------------------------------------------------

def _make_pdf(text: str) -> bytes:
    """Create a minimal single-page PDF containing `text`, return raw bytes."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=11)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)
    return buf.read()


RESUME_PDF = _make_pdf("Skills: Java, Linux Basics, Git")
JOB_PDF = _make_pdf(
    "Required: Kubernetes, CI/CD Pipeline, Microservices, System Design"
)


# ---------------------------------------------------------------------------
# Fixture: TestClient with lifespan (context manager triggers startup/shutdown)
# ---------------------------------------------------------------------------

@pytest.fixture(name="api")
def api_client():
    """Yield a TestClient that properly triggers the FastAPI lifespan."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Test 1 — Happy Path (Gemini returns structured output)
# ---------------------------------------------------------------------------

def test_happy_path(api):
    """Full flow with mocked Gemini returning structured skill lists."""

    def mock_gemini_extract(text, master_list):
        """Inspect text to decide which mock skill list to return."""
        if "Java" in text:
            return {"Java": "intermediate", "Linux Basics": "beginner", "Git": "intermediate"}
        return {"Kubernetes": "advanced", "CI/CD Pipeline": "intermediate", "Microservices": "advanced", "System Design": "advanced"}

    mock_summary = (
        "Great news! You already have a strong foundation in Java, Linux, "
        "and Git. Your roadmap has 7 skills across 4 phases."
    )

    with (
        patch(
            "app.gemini_client.extract_skills_groq",
            side_effect=mock_gemini_extract,
        ),
        patch(
            "app.roadmap.generate_summary_groq",
            return_value=mock_summary,
        ),
    ):
        response = api.post(
            "/analyze-gap",
            files={
                "resume": ("resume.pdf", RESUME_PDF, "application/pdf"),
                "job_description": ("job.pdf", JOB_PDF, "application/pdf"),
            },
        )

    assert response.status_code == 200
    data = response.json()

    # User skills should match the mocked resume extraction
    assert set(data["user_skills"]) == {"Java", "Linux Basics", "Git"}

    # All four JD skills should appear in required_skills
    assert "Kubernetes" in data["required_skills"]
    assert "CI/CD Pipeline" in data["required_skills"]

    # Missing skills should include JD skills the user lacks
    assert "Kubernetes" in data["missing_skills"]

    # Roadmap should have at least one tier
    assert len(data["roadmap"]["tiers"]) > 0

    # Summary should be the mocked Gemini response
    assert "Great news" in data["summary"]


# ---------------------------------------------------------------------------
# Test 2 — Fallback (Gemini fails, local parser + raw summary kick in)
# ---------------------------------------------------------------------------

def test_fallback_on_gemini_failure(api):
    """When Groq fails, the fallback parser and plain-text summary still return 200."""

    with (
        patch(
            "app.gemini_client.extract_skills_groq",
            side_effect=Exception("Groq API is down"),
        ),
        patch(
            "app.roadmap.generate_summary_groq",
            side_effect=Exception("Groq API is down"),
        ),
    ):
        response = api.post(
            "/analyze-gap",
            files={
                "resume": ("resume.pdf", RESUME_PDF, "application/pdf"),
                "job_description": ("job.pdf", JOB_PDF, "application/pdf"),
            },
        )

    assert response.status_code == 200
    data = response.json()

    # Fallback parser should still find skills via text matching
    assert len(data["user_skills"]) > 0, "Fallback should extract at least one skill"

    # Missing skills should be computed
    assert isinstance(data["missing_skills"], dict)

    # Fallback summary should be a non-empty plain-text string
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0

    # Roadmap structure should still be valid
    assert "tiers" in data["roadmap"]
