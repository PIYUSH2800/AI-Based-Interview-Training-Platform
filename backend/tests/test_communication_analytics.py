"""
test_communication_analytics.py

Tests for:
  1. Deterministic analytics service (unit tests)
  2. Analytics API endpoint (integration tests — auth, ownership, structure)
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
from app.services.communication_analytics import analyze_answer, compute_aggregate
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def _create_user(email="ana@example.com", name="Ana"):
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


def _create_interview(user_id, total_questions=2):
    db = TestingSessionLocal()
    interview = Interview(
        user_id=user_id,
        job_role="Software Developer",
        interview_type="Technical Interview",
        difficulty="Intermediate",
        mode="Text",
        total_questions=total_questions,
        overall_score=78.0,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    interview_id = interview.id
    db.close()
    return interview_id


def _add_question_answer(interview_id, seq, q_text, a_text):
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
        score=80.0,
        feedback="Good answer.",
    )
    db.add(a)
    db.commit()
    db.close()
    return qid


def _token(email="ana@example.com"):
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
#  UNIT TESTS — deterministic analytics service
# ════════════════════════════════════════════════════════════════════════════

class TestWordCount:
    def test_basic(self):
        result = analyze_answer("Hello I am a student")
        assert result["word_count"] == 5

    def test_punctuation_stripped(self):
        result = analyze_answer("Hello, world! How are you?")
        assert result["word_count"] == 5

    def test_empty_string(self):
        result = analyze_answer("")
        assert result["word_count"] == 0

    def test_whitespace_only(self):
        result = analyze_answer("   \n\t  ")
        assert result["word_count"] == 0


class TestSentenceCount:
    def test_single_sentence(self):
        result = analyze_answer("This is one sentence.")
        assert result["sentence_count"] == 1

    def test_multiple_sentences(self):
        result = analyze_answer("First sentence. Second sentence. Third one!")
        assert result["sentence_count"] == 3

    def test_question_mark(self):
        result = analyze_answer("What is REST? It is an architectural style.")
        assert result["sentence_count"] == 2

    def test_empty(self):
        result = analyze_answer("")
        assert result["sentence_count"] == 0

    def test_no_punctuation_counts_as_one(self):
        result = analyze_answer("No punctuation at the end")
        assert result["sentence_count"] == 1


class TestFillerDetection:
    def test_liked_does_not_match_like(self):
        """'liked' must NOT count as the filler 'like'."""
        result = analyze_answer("I liked the project and liked working on it.")
        assert result["filler_word_count"] == 0
        assert "like" not in result["detected_fillers"]

    def test_like_as_filler(self):
        result = analyze_answer("It was like a really good experience.")
        assert result["detected_fillers"].get("like", 0) >= 1

    def test_you_know_phrase(self):
        result = analyze_answer("You know it was a great project you know.")
        assert result["detected_fillers"].get("you know", 0) >= 1

    def test_multiple_fillers(self):
        result = analyze_answer("Um so basically I think like it was okay.")
        assert result["filler_word_count"] >= 3

    def test_um_detection(self):
        result = analyze_answer("Um I am not sure about this.")
        assert "um" in result["detected_fillers"]

    def test_no_fillers(self):
        result = analyze_answer(
            "The MVC pattern separates concerns into Model, View, and Controller layers."
        )
        assert result["filler_word_count"] == 0

    def test_filler_rate_calculation(self):
        # "um" appears once in a 10-word answer → rate = 10.0%
        result = analyze_answer("Um this is a test with exactly ten words here.")
        total = result["word_count"]
        fillers = result["filler_word_count"]
        expected_rate = round((fillers / total) * 100, 1)
        assert abs(result["filler_word_rate"] - expected_rate) < 0.01


class TestEstimatedSpeakingTime:
    def test_proportional_to_word_count(self):
        # 130 words → ~60 seconds at baseline 130 wpm
        text = " ".join(["word"] * 130)
        result = analyze_answer(text)
        # Should be approximately 60 seconds
        assert 55 <= result["estimated_speaking_time_seconds"] <= 65

    def test_zero_for_empty(self):
        result = analyze_answer("")
        assert result["estimated_speaking_time_seconds"] == 0


class TestEstimatedWPM:
    def test_wpm_nonzero_for_nonempty(self):
        result = analyze_answer("This is a test answer with several words in it.")
        assert result["estimated_wpm"] > 0

    def test_wpm_zero_for_empty(self):
        result = analyze_answer("")
        assert result["estimated_wpm"] == 0


class TestNoDivisionByZero:
    def test_empty_answer_all_zeros(self):
        result = analyze_answer("")
        for key in [
            "word_count",
            "sentence_count",
            "estimated_speaking_time_seconds",
            "estimated_wpm",
            "filler_word_count",
        ]:
            assert result[key] == 0
        assert result["filler_word_rate"] == 0.0
        assert result["detected_fillers"] == {}

    def test_single_word(self):
        result = analyze_answer("Hello")
        assert result["word_count"] == 1
        assert result["sentence_count"] == 1
        assert result["estimated_wpm"] > 0  # No ZeroDivisionError


class TestComputeAggregate:
    def test_empty_list(self):
        agg = compute_aggregate([])
        assert agg["total_words"] == 0
        assert agg["overall_suggestion"] != ""

    def test_totals_correct(self):
        stats = [
            {**analyze_answer("Hello world."), "filler_rate": 0.0},
            {**analyze_answer("Um this is a test."), "filler_rate": 20.0},
        ]
        agg = compute_aggregate(stats)
        assert agg["total_words"] == stats[0]["word_count"] + stats[1]["word_count"]
        assert agg["total_fillers" if "total_fillers" in agg else "total_filler_words"] >= 0

    def test_suggestion_high_filler_rate(self):
        # Artificially high filler rates → suggestion mentions filler words
        stats = [{"word_count": 10, "sentence_count": 1, "filler_word_count": 4,
                  "estimated_wpm": 130, "filler_rate": 40.0}]
        agg = compute_aggregate(stats)
        assert "filler" in agg["overall_suggestion"].lower()


# ════════════════════════════════════════════════════════════════════════════
#  INTEGRATION TESTS — analytics API endpoint
# ════════════════════════════════════════════════════════════════════════════

class TestAnalyticsEndpoint:
    def test_unauthenticated_returns_401(self):
        response = client.get("/api/interviews/999/communication-analytics")
        assert response.status_code == 401

    def test_wrong_user_returns_404(self):
        """User B cannot see User A's analytics."""
        uid_a = _create_user("usera@example.com", "UserA")
        uid_b = _create_user("userb@example.com", "UserB")
        interview_id = _create_interview(uid_a)
        _add_question_answer(
            interview_id, 1,
            "Tell me about yourself.",
            "I am a backend developer with three years of experience.",
        )

        # User B tries to access User A's interview
        response = client.get(
            f"/api/interviews/{interview_id}/communication-analytics",
            headers=_token("userb@example.com"),
        )
        assert response.status_code == 404

    def test_valid_request_returns_200_with_structure(self):
        uid = _create_user("valid@example.com", "Valid User")
        interview_id = _create_interview(uid)
        _add_question_answer(
            interview_id, 1,
            "Tell me about yourself.",
            "I am a software developer with experience in Python and FastAPI.",
        )
        _add_question_answer(
            interview_id, 2,
            "What is REST?",
            "REST is an architectural style for distributed systems using HTTP.",
        )

        response = client.get(
            f"/api/interviews/{interview_id}/communication-analytics",
            headers=_token("valid@example.com"),
        )
        assert response.status_code == 200
        data = response.json()

        # Top-level structure
        assert data["interview_id"] == interview_id
        assert "total_words" in data
        assert "total_sentences" in data
        assert "total_filler_words" in data
        assert "avg_filler_rate" in data
        assert "avg_wpm" in data
        assert "overall_suggestion" in data
        assert isinstance(data["per_question"], list)
        assert len(data["per_question"]) == 2

    def test_per_question_fields_present(self):
        uid = _create_user("fields@example.com", "Fields User")
        interview_id = _create_interview(uid, total_questions=1)
        answer_text = "Python uses dynamic typing and memory management via garbage collection."
        _add_question_answer(
            interview_id, 1, "What is Python?", answer_text
        )

        response = client.get(
            f"/api/interviews/{interview_id}/communication-analytics",
            headers=_token("fields@example.com"),
        )
        assert response.status_code == 200
        data = response.json()

        q = data["per_question"][0]
        expected_keys = [
            "question_id", "sequence_number", "question_text", "answer_text",
            "word_count", "sentence_count", "avg_sentence_length",
            "max_sentence_length", "estimated_speaking_time_seconds",
            "estimated_wpm", "filler_word_count", "filler_word_rate",
            "detected_fillers", "ai_feedback",
        ]
        for key in expected_keys:
            assert key in q, f"Missing key: {key}"

        # word_count must be non-zero for non-empty answer
        assert q["word_count"] > 0
        # ai_feedback should have the 4 qualitative fields
        fb = q["ai_feedback"]
        assert fb is not None
        for fb_key in ["directness", "structure", "conciseness", "suggestion"]:
            assert fb_key in fb

    def test_interview_with_no_answers_returns_empty_list(self):
        uid = _create_user("noanswer@example.com", "NoAnswer")
        interview_id = _create_interview(uid, total_questions=1)
        # Add question but NO answer
        db = TestingSessionLocal()
        q = Question(
            interview_id=interview_id,
            question_text="What is polymorphism?",
            question_type="Technical Interview",
            difficulty="Intermediate",
            sequence_number=1,
        )
        db.add(q)
        db.commit()
        db.close()

        response = client.get(
            f"/api/interviews/{interview_id}/communication-analytics",
            headers=_token("noanswer@example.com"),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["per_question"] == []
        assert data["total_words"] == 0
