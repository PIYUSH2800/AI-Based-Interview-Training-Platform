"""
test_adaptive_questions.py

Tests for Checkpoint 7A — Adaptive AI Interview Questions:
  1. Unit tests for difficulty scaling and mock deduplication.
  2. Integration tests for /api/ai/generate-question with interview_id session history.
  3. Ownership enforcement and fallback handling.
"""

import os
import sys

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, Interview, Question, Answer
from app.auth.auth import create_access_token, get_password_hash
from app.api.ai_routes import adjust_difficulty, normalize_difficulty
from app.services.mock_ai_service import generate_adaptive_question_mock
from app.services.ai_service import ai_service
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def _create_user(email="test@example.com", name="Test User"):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=get_password_hash("password"),
            education="B.Tech",
            experience_level="Intermediate",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    user_id = user.id
    db.close()
    return user_id


def _create_interview(user_id, job_role="Software Developer", difficulty="Intermediate"):
    db = TestingSessionLocal()
    interview = Interview(
        user_id=user_id,
        job_role=job_role,
        interview_type="Technical Interview",
        difficulty=difficulty,
        mode="Text",
        total_questions=3,
        overall_score=None,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    interview_id = interview.id
    db.close()
    return interview_id


def _add_question_and_answer(interview_id, seq, q_text, a_text, score=80.0):
    db = TestingSessionLocal()
    q = Question(
        interview_id=interview_id,
        question_text=q_text,
        question_type="Technical Interview",
        difficulty="Intermediate",
        sequence_number=seq,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    qid = q.id

    a = Answer(
        question_id=qid,
        answer_text=a_text,
        score=score,
        technical_score=score,
        communication_score=score,
        relevance_score=score,
        completeness_score=score,
        feedback="Good answer.",
    )
    db.add(a)
    db.commit()
    db.close()
    return qid


def _token(email="test@example.com"):
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
#  UNIT TESTS — Difficulty adaptation & Mock deduplication
# ════════════════════════════════════════════════════════════════════════════

class TestDifficultyAdaptationUnit:
    def test_normalize_difficulty(self):
        assert normalize_difficulty("easy") == "Easy"
        assert normalize_difficulty("basic") == "Easy"
        assert normalize_difficulty("hard") == "Hard"
        assert normalize_difficulty("advanced") == "Hard"
        assert normalize_difficulty("intermediate") == "Intermediate"
        assert normalize_difficulty("unknown") == "Intermediate"

    def test_step_up_on_high_score(self):
        assert adjust_difficulty("Easy", 90.0) == "Intermediate"
        assert adjust_difficulty("Intermediate", 85.0) == "Hard"
        assert adjust_difficulty("Hard", 95.0) == "Hard"  # Max limit

    def test_step_down_on_low_score(self):
        assert adjust_difficulty("Hard", 45.0) == "Intermediate"
        assert adjust_difficulty("Intermediate", 30.0) == "Easy"
        assert adjust_difficulty("Easy", 20.0) == "Easy"  # Min limit

    def test_maintain_on_moderate_score(self):
        assert adjust_difficulty("Intermediate", 70.0) == "Intermediate"
        assert adjust_difficulty("Easy", 60.0) == "Easy"
        assert adjust_difficulty("Hard", 75.0) == "Hard"


class TestMockDeduplicationUnit:
    def test_skips_previous_questions(self):
        prev_q = "Explain the difference between a list and a tuple in Python."
        result = generate_adaptive_question_mock(
            job_role="Software Developer",
            interview_type="Technical Interview",
            difficulty="Intermediate",
            skills="Python",
            previous_questions=[prev_q],
        )
        assert result["question"].strip().lower() != prev_q.strip().lower()
        assert "question" in result
        assert "difficulty" in result


# ════════════════════════════════════════════════════════════════════════════
#  INTEGRATION TESTS — /api/ai/generate-question with adaptive context
# ════════════════════════════════════════════════════════════════════════════

class TestAdaptiveQuestionAPI:
    def test_unauthenticated_returns_401(self):
        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "interview_id": 999,
            },
        )
        assert response.status_code == 401

    def test_wrong_user_returns_404(self):
        uid_a = _create_user("usera_adapt@example.com", "UserA")
        uid_b = _create_user("userb_adapt@example.com", "UserB")
        interview_id = _create_interview(uid_a)

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "interview_id": interview_id,
            },
            headers=_token("userb_adapt@example.com"),
        )
        assert response.status_code == 404

    def test_first_question_adaptive_request(self):
        uid = _create_user("user_first@example.com", "User First")
        interview_id = _create_interview(uid, difficulty="Easy")

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Easy",
                "interview_id": interview_id,
            },
            headers=_token("user_first@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert len(data["question"]) > 5
        assert "difficulty" in data
        assert "reason" in data

    def test_adaptive_question_steps_up_on_high_performance(self):
        uid = _create_user("user_high@example.com", "High Performer")
        interview_id = _create_interview(uid, difficulty="Easy")

        _add_question_and_answer(
            interview_id,
            seq=1,
            q_text="What is Python?",
            a_text="Python is a high-level interpreted programming language with dynamic typing and simple syntax.",
            score=95.0,  # High score -> difficulty should scale up to Intermediate
        )

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Easy",
                "interview_id": interview_id,
            },
            headers=_token("user_high@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty"] == "Intermediate"
        assert data["question"] != "What is Python?"

    def test_adaptive_question_steps_down_on_low_performance(self):
        uid = _create_user("user_low@example.com", "Low Performer")
        interview_id = _create_interview(uid, difficulty="Hard")

        _add_question_and_answer(
            interview_id,
            seq=1,
            q_text="Explain GIL in Python.",
            a_text="I don't know.",
            score=30.0,  # Low score -> difficulty should scale down to Intermediate
        )

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Hard",
                "interview_id": interview_id,
            },
            headers=_token("user_low@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty"] == "Intermediate"
        assert data["question"] != "Explain GIL in Python."
