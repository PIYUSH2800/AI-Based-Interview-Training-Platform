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


# ════════════════════════════════════════════════════════════════════════════
#  REGRESSION TESTS — Bug Fix: Null Profile Skills & AI Fallback Verification
# ════════════════════════════════════════════════════════════════════════════

from unittest.mock import patch, MagicMock
from app.models.models import Profile

class TestQuestionGenerationRegression:
    def test_null_profile_skills_does_not_crash(self):
        """Verify that a user with profile.skills=None generates a question successfully."""
        uid = _create_user("user_nullskills@example.com", "Null Skills User")

        # Explicitly ensure profile has None for skills
        db = TestingSessionLocal()
        prof = db.query(Profile).filter(Profile.user_id == uid).first()
        if not prof:
            prof = Profile(user_id=uid, skills=None, degree=None)
            db.add(prof)
        else:
            prof.skills = None
        db.commit()
        db.close()

        interview_id = _create_interview(uid, job_role="Software Developer")

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "skills": "",
                "interview_id": interview_id,
            },
            headers=_token("user_nullskills@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert len(data["question"]) > 5
        assert data["difficulty"] == "Intermediate"

    def test_gemini_success_mocked(self):
        """Verify successful Gemini question generation returns expected format."""
        uid = _create_user("user_gemini_ok@example.com", "Gemini User")
        interview_id = _create_interview(uid)

        mock_gemini_result = {
            "question": "Explain how virtual DOM works in React.",
            "difficulty": "Intermediate",
            "topic": "React",
            "category": "Technical Interview",
            "reason": "Targeted React framework question.",
        }

        with patch.object(ai_service.real_ai, "is_configured", return_value=True), \
             patch.object(ai_service, "is_ai_enabled", return_value=True), \
             patch.object(ai_service.real_ai, "generate_adaptive_question", return_value=mock_gemini_result):
            response = client.post(
                "/api/ai/generate-question",
                json={
                    "job_role": "Frontend Developer",
                    "interview_type": "Technical Interview",
                    "difficulty": "Intermediate",
                    "interview_id": interview_id,
                },
                headers=_token("user_gemini_ok@example.com"),
            )
            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "Explain how virtual DOM works in React."
            assert data["topic"] == "React"

    def test_gemini_failure_fallback_to_mock(self):
        """Verify that when Gemini raises an exception, fallback to Mock AI succeeds."""
        uid = _create_user("user_gemini_fail@example.com", "Gemini Fail User")
        interview_id = _create_interview(uid)

        with patch.object(ai_service.real_ai, "is_configured", return_value=True), \
             patch.object(ai_service, "is_ai_enabled", return_value=True), \
             patch.object(ai_service, "is_fallback_enabled", return_value=True), \
             patch.object(ai_service.real_ai, "generate_adaptive_question", side_effect=RuntimeError("Gemini API connection timeout")):
            response = client.post(
                "/api/ai/generate-question",
                json={
                    "job_role": "Software Developer",
                    "interview_type": "Technical Interview",
                    "difficulty": "Intermediate",
                    "interview_id": interview_id,
                },
                headers=_token("user_gemini_fail@example.com"),
            )
            assert response.status_code == 200
            data = response.json()
            assert "question" in data
            assert len(data["question"]) > 5
            assert "difficulty" in data

    def test_mock_only_operation(self):
        """Verify question generation works smoothly in mock-only mode."""
        uid = _create_user("user_mockonly@example.com", "Mock Only User")
        interview_id = _create_interview(uid)

        with patch.object(ai_service, "is_ai_enabled", return_value=False):
            response = client.post(
                "/api/ai/generate-question",
                json={
                    "job_role": "Software Developer",
                    "interview_type": "Technical Interview",
                    "difficulty": "Intermediate",
                    "interview_id": interview_id,
                },
                headers=_token("user_mockonly@example.com"),
            )
            assert response.status_code == 200
            data = response.json()
            assert "question" in data
            assert len(data["question"]) > 5

    def test_invalid_interview_id_returns_404(self):
        """Verify calling with non-existent interview returns 404."""
        uid = _create_user("user_invalid_int@example.com", "Invalid Int User")

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "interview_id": 9999999,
            },
            headers=_token("user_invalid_int@example.com"),
        )
        assert response.status_code == 404

    def test_response_contract_matches_frontend_expectations(self):
        """Verify all response fields expected by frontend exist and are non-empty strings."""
        uid = _create_user("user_contract@example.com", "Contract User")
        interview_id = _create_interview(uid)

        response = client.post(
            "/api/ai/generate-question",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "interview_id": interview_id,
            },
            headers=_token("user_contract@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data.get("question"), str) and len(data["question"]) > 0
        assert isinstance(data.get("difficulty"), str) and len(data["difficulty"]) > 0
        assert isinstance(data.get("topic"), str) and len(data["topic"]) > 0
        assert isinstance(data.get("category"), str) and len(data["category"]) > 0
        assert isinstance(data.get("reason"), str) and len(data["reason"]) > 0

    def test_full_3_question_interview_flow(self):
        """Simulate the complete 3-question interview flow from frontend perspective."""
        uid = _create_user("user_fullflow@example.com", "Full Flow User")
        token = _token("user_fullflow@example.com")

        # 1. Create interview
        create_res = client.post(
            "/api/interviews",
            json={
                "job_role": "Software Developer",
                "interview_type": "Technical Interview",
                "difficulty": "Intermediate",
                "mode": "Text",
                "total_questions": 3,
            },
            headers=token,
        )
        assert create_res.status_code == 200
        interview_id = create_res.json()["id"]

        for q_idx in range(3):
            # Generate question
            gen_res = client.post(
                "/api/ai/generate-question",
                json={
                    "job_role": "Software Developer",
                    "interview_type": "Technical Interview",
                    "difficulty": "Intermediate",
                    "skills": "",
                    "interview_id": interview_id,
                },
                headers=token,
            )
            assert gen_res.status_code == 200
            q_data = gen_res.json()
            assert len(q_data["question"]) > 5

            # Save question
            save_q_res = client.post(
                f"/api/interviews/{interview_id}/questions",
                json={
                    "question_text": q_data["question"],
                    "question_type": "Technical Interview",
                    "difficulty": q_data["difficulty"],
                    "topic": q_data["topic"],
                    "sequence_number": q_idx + 1,
                },
                headers=token,
            )
            assert save_q_res.status_code == 200
            q_id = save_q_res.json()["id"]

            # Submit answer
            eval_res = client.post(
                "/api/ai/evaluate-answer",
                json={
                    "question_text": q_data["question"],
                    "answer_text": "A list in Python is mutable while a tuple is immutable.",
                },
                headers=token,
            )
            assert eval_res.status_code == 200
            evaluation = eval_res.json()

            ans_res = client.post(
                f"/api/interviews/{interview_id}/questions/{q_id}/answers",
                json={
                    "answer_text": "A list in Python is mutable while a tuple is immutable.",
                    "score": evaluation["score"],
                    "technical_score": evaluation["technical_score"],
                    "communication_score": evaluation["communication_score"],
                    "relevance_score": evaluation["relevance_score"],
                    "completeness_score": evaluation["completeness_score"],
                    "feedback": evaluation["feedback"],
                },
                headers=token,
            )
            assert ans_res.status_code == 200

        # Complete interview
        comp_res = client.post(
            f"/api/interviews/{interview_id}/complete",
            json={"duration": 180},
            headers=token,
        )
        assert comp_res.status_code == 200
        assert comp_res.json()["duration"] == 180
