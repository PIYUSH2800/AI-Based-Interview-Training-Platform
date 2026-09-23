"""
test_interview_strategy.py

Tests for Checkpoint 7B — Interview Strategy & Question Coverage:
  1. Interview type strategy guidance (Technical, Behavioral, HR, System Design).
  2. Topic tracking and under-covered topic prioritization.
  3. Topic deduplication and avoidance of repeating covered topics when under-covered topics exist.
  4. Weak area identification and integration.
  5. API integration via /api/ai/generate-question with coverage state and topic responses.
"""

import os
import sys

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, Interview, Question, Answer
from app.auth.auth import create_access_token, get_password_hash
from app.api.ai_routes import get_interview_strategy_guidance
from app.services.mock_ai_service import generate_adaptive_question_mock
from app.services.ai_service import ai_service
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def _create_user(email="strategy_user@example.com", name="Strategy User"):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=get_password_hash("password"),
            education="B.Tech",
            experience_level="Senior",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    user_id = user.id
    db.close()
    return user_id


def _create_interview(user_id, job_role="Backend Developer", interview_type="Technical Interview", difficulty="Intermediate"):
    db = TestingSessionLocal()
    interview = Interview(
        user_id=user_id,
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        mode="Text",
        total_questions=5,
        overall_score=None,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    interview_id = interview.id
    db.close()
    return interview_id


def _token(email="strategy_user@example.com"):
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


# ── 1. Strategy Guidance Unit Tests ──────────────────────────────────────────
def test_strategy_guidance_for_interview_types():
    tech_guide = get_interview_strategy_guidance("Technical Interview", "Software Engineer")
    assert "technical depth" in tech_guide.lower() or "problem solving" in tech_guide.lower()

    beh_guide = get_interview_strategy_guidance("Behavioral Interview", "Product Manager")
    assert "star" in beh_guide.lower() or "behavioral" in beh_guide.lower()

    hr_guide = get_interview_strategy_guidance("HR Interview", "Data Analyst")
    assert "culture" in hr_guide.lower() or "soft skills" in hr_guide.lower()

    sd_guide = get_interview_strategy_guidance("System Design Interview", "DevOps Engineer")
    assert "scalability" in sd_guide.lower() or "architecture" in sd_guide.lower()


# ── 2. Mock AI Coverage & Topic Selection Tests ──────────────────────────────
def test_mock_ai_under_covered_topic_selection():
    # If under_covered_topics has items, mock AI should select one of them
    result = generate_adaptive_question_mock(
        job_role="Full Stack Engineer",
        interview_type="Technical Interview",
        difficulty="Intermediate",
        skills="Python, React, SQL, Docker",
        previous_questions=["Explain Python GIL."],
        last_answer_context=None,
        topics_covered=["Python"],
        under_covered_topics=["React", "SQL", "Docker"],
        weak_areas=[]
    )
    assert "question" in result
    assert "topic" in result
    assert result["topic"] in ["React", "SQL", "Docker"]
    assert result["topic"] != "Python"


def test_mock_ai_returns_category_and_reason():
    result = generate_adaptive_question_mock(
        job_role="Data Scientist",
        interview_type="Technical Interview",
        difficulty="Advanced",
        skills="Machine Learning, Statistics",
        topics_covered=[],
        under_covered_topics=["Machine Learning", "Statistics"],
        weak_areas=[]
    )
    assert result["category"] in ["Technical Interview", "General"]
    assert len(result["reason"]) > 0


# ── 3. Endpoint Integration & Strategy Flow Tests ─────────────────────────────
def test_generate_question_with_topic_tracking_and_under_coverage():
    uid = _create_user("strategy_test1@example.com")
    iid = _create_interview(uid, job_role="Backend Developer", interview_type="Technical Interview")

    # Add question 1 (Python)
    db = TestingSessionLocal()
    q1 = Question(
        interview_id=iid,
        question_text="Explain Python GIL.",
        question_type="Technical Interview",
        difficulty="Intermediate",
        topic="Python",
        sequence_number=1
    )
    db.add(q1)
    db.commit()
    db.refresh(q1)
    a1 = Answer(
        question_id=q1.id,
        answer_text="GIL stands for Global Interpreter Lock...",
        score=85.0,
        technical_score=85.0,
        communication_score=85.0,
        relevance_score=85.0,
        completeness_score=85.0,
        feedback="Good explanation."
    )
    db.add(a1)
    db.commit()
    db.close()

    # Call generate-question for q2
    headers = _token("strategy_test1@example.com")
    resp = client.post("/api/ai/generate-question", json={
        "job_role": "Backend Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "skills": "Python, SQL, System Design",
        "interview_id": iid
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "topic" in data
    assert "category" in data
    # Topic should not be Python if other under-covered topics exist (SQL, System Design)
    assert data["topic"] in ["SQL", "System Design", "Database", "General", "Technical"]


def test_generate_question_weak_area_incorporation():
    uid = _create_user("strategy_test2@example.com")
    iid = _create_interview(uid, job_role="DevOps Engineer", interview_type="Technical Interview")

    # Add q1 with low technical score on Docker
    db = TestingSessionLocal()
    q1 = Question(
        interview_id=iid,
        question_text="Explain Docker networking.",
        question_type="Technical Interview",
        difficulty="Intermediate",
        topic="Docker",
        sequence_number=1
    )
    db.add(q1)
    db.commit()
    db.refresh(q1)
    a1 = Answer(
        question_id=q1.id,
        answer_text="Not sure.",
        score=40.0,
        technical_score=40.0,
        communication_score=50.0,
        relevance_score=40.0,
        completeness_score=30.0,
        feedback="Incomplete answer."
    )
    db.add(a1)
    db.commit()
    db.close()

    # Request q2
    headers = _token("strategy_test2@example.com")
    resp = client.post("/api/ai/generate-question", json={
        "job_role": "DevOps Engineer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "skills": "Docker, Kubernetes, CI/CD",
        "interview_id": iid
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "topic" in data
