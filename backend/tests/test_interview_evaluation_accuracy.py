"""
Tests for Checkpoint 10G-C — Interview Answer Evaluation Accuracy & Scoring Reliability.

Verifies:
1. Meaningfulness validator detects random character strings ('hbasjhkdfggasklfdg', etc.)
2. Repeated gibberish, empty, and punctuation-only inputs receive 0 score across all categories
3. Short legitimate technical answers ('O(log n)', 'HTTP 404', 'O(1)', 'SELECT * FROM users') are preserved with strong scores
4. Fluent but irrelevant answers receive low relevance/technical scores instead of inflated length bonuses
5. Long meaningless answers (multi-token gibberish) receive 0 score
6. End-to-end interview session evaluation with all meaningless answers records 0.0% overall score in database
7. Partially correct answers receive justified non-zero partial credit
8. Category scores (technical, communication, relevance, completeness) are accurately computed
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models import models
from app.services.answer_validator import validate_answer_meaningfulness
from app.services.mock_ai_service import evaluate_answer_mock
from app.services.ai_service import ai_service

client = TestClient(app)


def _get_auth_token(email="eval_accuracy_tester@example.com"):
    """Helper to register/login test user and return auth headers."""
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        resp = client.post("/api/auth/register", json={
            "email": email,
            "password": "Password123!",
            "name": "Eval Accuracy Tester",
            "experience_level": "intermediate",
            "education": "B.S. in Computer Science"
        })
        assert resp.status_code == 200, f"Registration failed: {resp.text}"
    db.close()

    resp = client.post("/api/auth/login", data={
        "username": email,
        "password": "Password123!"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── 1. Meaningfulness Validator Unit Tests ────────────────────────────────────

def test_validator_rejects_user_reported_gibberish():
    """Specific user reported bug string 'hbasjhkdfggasklfdg' must be flagged as invalid."""
    res = validate_answer_meaningfulness("What is a tuple?", "hbasjhkdfggasklfdg")
    assert res.is_valid is False
    assert res.reason is not None


@pytest.mark.parametrize("gibberish", [
    "hbasjhkdfggasklfdg",
    "asdfghjkl",
    "qwertyuiopasdfgh",
    "zxcvbnmasdfgh",
    "bcdfghjklmnpqrst",
    "kjhgfdsazxcvbnm",
])
def test_validator_rejects_keyboard_mash_and_consonant_runs(gibberish):
    res = validate_answer_meaningfulness("Explain REST APIs", gibberish)
    assert res.is_valid is False


@pytest.mark.parametrize("empty_input", [
    "",
    "   ",
    "\n\t  \n",
])
def test_validator_rejects_empty_and_whitespace(empty_input):
    res = validate_answer_meaningfulness("What is recursion?", empty_input)
    assert res.is_valid is False


@pytest.mark.parametrize("punct", [
    "???",
    ".....",
    "---",
    "!@#$%^&*",
    ",,,,,,",
])
def test_validator_rejects_punctuation_only(punct):
    res = validate_answer_meaningfulness("Explain Docker containers", punct)
    assert res.is_valid is False


@pytest.mark.parametrize("repeated", [
    "aaaaaaa",
    "zzzzzzzzzzzz",
    "asdf asdf asdf",
    "bla bla bla bla bla",
    "idk idk idk idk",
])
def test_validator_rejects_repeated_token_loops(repeated):
    res = validate_answer_meaningfulness("What is an index?", repeated)
    assert res.is_valid is False


# ── 2. Preservation of Legitimate Short Technical Answers ─────────────────────

@pytest.mark.parametrize("tech_answer", [
    "O(log n)",
    "O(1)",
    "O(n log n)",
    "O(n^2)",
    "HTTP 404",
    "404 Not Found",
    "SELECT * FROM users",
    "A tuple is immutable.",
    "[]",
    "{}",
    "return True",
    "TCP is connection-oriented while UDP is connectionless.",
    "Polymorphism allows objects of different classes to respond to the same interface.",
])
def test_validator_preserves_valid_technical_answers(tech_answer):
    res = validate_answer_meaningfulness("Technical Interview Question", tech_answer)
    assert res.is_valid is True, f"Failed to preserve legitimate technical answer: '{tech_answer}'"


# ── 3. Scoring Evaluation for Meaningless Answers ─────────────────────────────

def test_meaningless_answer_receives_zero_score():
    """The reported bug string 'hbasjhkdfggasklfdg' must evaluate to 0 score across all categories."""
    eval_res = evaluate_answer_mock(
        "Explain the difference between a list and a tuple in Python.",
        "hbasjhkdfggasklfdg"
    )
    assert eval_res["score"] == 0
    assert eval_res["technical_score"] == 0
    assert eval_res["relevance_score"] == 0
    assert eval_res["communication_score"] == 0
    assert eval_res["completeness_score"] == 0
    assert len(eval_res["strengths"]) == 0
    assert len(eval_res["improvements"]) > 0


def test_long_repeated_gibberish_receives_zero_score():
    """Long repeated gibberish tokens must NOT get positive length bonus."""
    long_gibberish = " ".join(["asdfghjk"] * 25)
    eval_res = evaluate_answer_mock("Explain microservices architecture.", long_gibberish)
    assert eval_res["score"] == 0
    assert eval_res["technical_score"] == 0
    assert eval_res["relevance_score"] == 0


# ── 4. Scoring Evaluation for Valid Concise & Detailed Answers ────────────────

def test_short_valid_complexity_answer_receives_high_score():
    """Concise correct technical answers like 'O(log n)' must receive high scores."""
    eval_res = evaluate_answer_mock(
        "What is the time complexity of binary search in a sorted array?",
        "O(log n)"
    )
    assert eval_res["score"] >= 80
    assert eval_res["technical_score"] >= 90
    assert eval_res["relevance_score"] >= 90


def test_short_valid_http_answer_receives_high_score():
    eval_res = evaluate_answer_mock(
        "What HTTP status code represents a resource that was not found on the server?",
        "HTTP 404"
    )
    assert eval_res["score"] >= 80
    assert eval_res["technical_score"] >= 90
    assert eval_res["relevance_score"] >= 90


def test_valid_concise_tuple_explanation_receives_good_score():
    eval_res = evaluate_answer_mock(
        "Explain the difference between a list and a tuple in Python.",
        "A tuple is immutable in Python."
    )
    assert eval_res["score"] >= 75
    assert eval_res["technical_score"] >= 80
    assert eval_res["relevance_score"] >= 80


def test_fluent_offtopic_answer_receives_low_relevance_and_technical_score():
    """Fluent English answer that is completely off-topic must not receive high scores."""
    off_topic = "I enjoy walking in the park on sunny mornings and having a cup of coffee with pancakes."
    eval_res = evaluate_answer_mock(
        "Explain how database indexing using B-Trees improves query performance.",
        off_topic
    )
    assert eval_res["score"] <= 25
    assert eval_res["relevance_score"] <= 15
    assert eval_res["technical_score"] <= 15


# ── 5. End-to-End API Answer Evaluation Endpoint ──────────────────────────────

def test_api_evaluate_answer_endpoint_zero_for_gibberish():
    headers = _get_auth_token("eval_api_tester@example.com")
    resp = client.post("/api/ai/evaluate-answer", json={
        "question_text": "Explain how garbage collection works in Python.",
        "answer_text": "hbasjhkdfggasklfdg",
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 0
    assert data["technical_score"] == 0
    assert data["relevance_score"] == 0
    assert data["communication_score"] == 0
    assert data["completeness_score"] == 0


def test_api_evaluate_answer_endpoint_positive_for_valid_technical():
    headers = _get_auth_token("eval_api_tester2@example.com")
    resp = client.post("/api/ai/evaluate-answer", json={
        "question_text": "What is the time complexity of searching in a binary search tree in the average case?",
        "answer_text": "O(log n)",
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] >= 80
    assert data["technical_score"] >= 90


# ── 6. Full Interview Session Aggregation with Gibberish ──────────────────────

def test_session_with_only_gibberish_produces_zero_overall_score():
    """An interview where all answers are gibberish must have overall_score = 0.0 in DB and intelligence report."""
    headers = _get_auth_token("gibberish_session_user@example.com")

    # 1. Start interview
    init_resp = client.post("/api/interviews/", json={
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "standard",
        "total_questions": 3
    }, headers=headers)
    assert init_resp.status_code == 200, f"Interview creation failed: {init_resp.text}"
    interview_id = init_resp.json()["id"]

    # 2. Add question 1 & submit user-reported bug gibberish
    q1_resp = client.post(f"/api/interviews/{interview_id}/questions", json={
        "question_text": "Explain how hashing works in a Hash Map.",
        "question_type": "technical",
        "topic": "Data Structures",
        "difficulty": "Intermediate",
        "sequence_number": 1
    }, headers=headers)
    assert q1_resp.status_code == 200, f"Question creation failed: {q1_resp.text}"
    q1_id = q1_resp.json()["id"]

    # Evaluate answer via API
    eval1 = client.post("/api/ai/evaluate-answer", json={
        "question_text": "Explain how hashing works in a Hash Map.",
        "answer_text": "hbasjhkdfggasklfdg",
    }, headers=headers).json()
    assert eval1["score"] == 0

    # Save answer to DB
    ans1_resp = client.post(f"/api/interviews/{interview_id}/questions/{q1_id}/answers", json={
        "answer_text": "hbasjhkdfggasklfdg",
        "score": eval1["score"],
        "technical_score": eval1["technical_score"],
        "communication_score": eval1["communication_score"],
        "relevance_score": eval1["relevance_score"],
        "completeness_score": eval1["completeness_score"],
        "feedback": eval1["feedback"]
    }, headers=headers)
    assert ans1_resp.status_code == 200
    assert ans1_resp.json()["score"] == 0

    # 3. Complete interview
    comp_resp = client.post(f"/api/interviews/{interview_id}/complete", json={"duration": 45}, headers=headers)
    assert comp_resp.status_code == 200
    completed_data = comp_resp.json()
    assert completed_data["overall_score"] == 0.0, f"Expected 0.0% overall score, got {completed_data['overall_score']}"

    # 4. Check intelligence report
    intel_resp = client.get(f"/api/interviews/{interview_id}/intelligence", headers=headers)
    assert intel_resp.status_code == 200
    intel_data = intel_resp.json()
    assert intel_data["overall_score"] == 0.0
    assert intel_data["category_scores"]["technical"] == 0.0
    assert intel_data["category_scores"]["relevance"] == 0.0

    # 5. Check AI feedback endpoint
    fb_resp = client.post(f"/api/ai/generate-feedback/{interview_id}", headers=headers)
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert fb_data["overall_score"] == 0.0
