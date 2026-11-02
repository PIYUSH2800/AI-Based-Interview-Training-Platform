"""
test_extended_sessions.py

Tests for Checkpoint 10B — Extended AI Interview Sessions:
  1. Validation and acceptance of allowed question counts (3, 5, 10, 15, 20).
  2. Rejection of zero, negative, and unsupported question counts.
  3. No duplicate questions in 20-question mock sequences across all 5 supported roles and interview types.
  4. Complete 15-question end-to-end mock interview session, completion, and analytics.
  5. Complete 20-question end-to-end mock interview session, completion, and analytics.
  6. Existing 3, 5, and 10-question sessions remain intact and fully functional.
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
from app.services.mock_ai_service import generate_adaptive_question_mock, QUESTIONS_BANK
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def _get_or_create_user(email="extended_user@example.com", name="Extended User"):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=get_password_hash("testpassword"),
            education="B.Tech Computer Science",
            experience_level="Intermediate",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    uid = user.id
    db.close()
    return uid


def _auth_header(email="extended_user@example.com"):
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


# ── 1. Validation of Allowed Question Counts ─────────────────────────────────

@pytest.mark.parametrize("count", [3, 5, 10, 15, 20])
def test_allowed_question_counts(count):
    email = f"user_count_{count}@example.com"
    _get_or_create_user(email=email)
    headers = _auth_header(email)

    resp = client.post("/api/interviews", headers=headers, json={
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": count,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == count
    assert "id" in data


# ── 2. Rejection of Invalid Question Counts ──────────────────────────────────

@pytest.mark.parametrize("invalid_count", [0, -1, -5, 1, 2, 4, 7, 12, 18, 25, 100])
def test_rejected_question_counts(invalid_count):
    email = "user_invalid_counts@example.com"
    _get_or_create_user(email=email)
    headers = _auth_header(email)

    resp = client.post("/api/interviews", headers=headers, json={
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": invalid_count,
    })
    # Must be rejected as client error (422 validation error or 400 bad request)
    assert resp.status_code in [400, 422]


# ── 3. Mock AI Uniqueness in 20-Question Sequences Across All Roles ──────────

SUPPORTED_ROLES = [
    "Software Developer",
    "Data Scientist",
    "Data Analyst",
    "AI/ML Engineer",
    "Product Manager",
]

@pytest.mark.parametrize("role", SUPPORTED_ROLES)
def test_mock_ai_20_question_uniqueness_per_role(role):
    """Verifies Mock AI produces 20 unique questions for each supported job role."""
    asked = []
    for seq in range(1, 21):
        res = generate_adaptive_question_mock(
            job_role=role,
            interview_type="Technical Interview",
            difficulty="Intermediate",
            previous_questions=asked,
        )
        q_text = res["question"].strip()
        assert q_text not in asked, f"Role {role} generated duplicate question at seq {seq}: '{q_text}'"
        assert len(q_text) > 15
        asked.append(q_text)

    assert len(asked) == 20
    assert len(set(asked)) == 20


@pytest.mark.parametrize("itype", ["System Design Interview", "Behavioral Interview", "HR Interview"])
def test_mock_ai_20_question_uniqueness_per_interview_type(itype):
    """Verifies Mock AI produces 20 unique questions for distinct interview types."""
    asked = []
    for seq in range(1, 21):
        res = generate_adaptive_question_mock(
            job_role="Software Developer",
            interview_type=itype,
            difficulty="Intermediate",
            previous_questions=asked,
        )
        q_text = res["question"].strip()
        assert q_text not in asked, f"Interview type {itype} generated duplicate question at seq {seq}: '{q_text}'"
        asked.append(q_text)

    assert len(asked) == 20
    assert len(set(asked)) == 20


# ── 4. End-to-End 15-Question Mock Interview Session ─────────────────────────

def test_complete_15_question_mock_interview():
    email = "user_15_questions@example.com"
    _get_or_create_user(email=email)
    headers = _auth_header(email)

    # 1. Create 15-question interview
    create_res = client.post("/api/interviews", headers=headers, json={
        "job_role": "Data Scientist",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": 15,
    })
    assert create_res.status_code == 200
    interview_id = create_res.json()["id"]

    generated_questions = []

    # 2. Sequentially generate, save, and answer all 15 questions
    for seq in range(1, 16):
        gen_res = client.post("/api/ai/generate-question", headers=headers, json={
            "job_role": "Data Scientist",
            "interview_type": "Technical Interview",
            "difficulty": "Intermediate",
            "skills": "Python, Machine Learning",
            "interview_id": interview_id,
        })
        assert gen_res.status_code == 200
        gen_data = gen_res.json()
        q_text = gen_data["question"]

        # Verify question is unique
        assert q_text not in generated_questions, f"Duplicate question at sequence {seq}: {q_text}"
        generated_questions.append(q_text)

        # Save question
        save_q_res = client.post(f"/api/interviews/{interview_id}/questions", headers=headers, json={
            "question_text": q_text,
            "question_type": "Technical Interview",
            "difficulty": gen_data.get("difficulty", "Intermediate"),
            "topic": gen_data.get("topic", "Data Science"),
            "sequence_number": seq,
        })
        assert save_q_res.status_code == 200
        qid = save_q_res.json()["id"]

        # Submit answer
        ans_res = client.post(f"/api/interviews/{interview_id}/questions/{qid}/answers", headers=headers, json={
            "answer_text": f"This is my detailed technical explanation for question {seq} regarding {gen_data.get('topic')}. In practice we apply best practices.",
            "score": 80.0,
            "technical_score": 80.0,
            "communication_score": 85.0,
            "relevance_score": 80.0,
            "completeness_score": 75.0,
            "feedback": f"Good answer for question {seq}.",
        })
        assert ans_res.status_code == 200

    assert len(generated_questions) == 15
    assert len(set(generated_questions)) == 15

    # 3. Complete interview
    comp_res = client.post(f"/api/interviews/{interview_id}/complete", headers=headers, json={"duration": 900})
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["overall_score"] == 80.0
    assert comp_data["duration"] == 900

    # 4. Verify all 15 questions present in details
    det_res = client.get(f"/api/interviews/{interview_id}/details", headers=headers)
    assert det_res.status_code == 200
    assert len(det_res.json()["questions"]) == 15

    # 5. Verify communication analytics include all 15 questions
    comm_res = client.get(f"/api/interviews/{interview_id}/communication-analytics", headers=headers)
    assert comm_res.status_code == 200
    comm_data = comm_res.json()
    assert len(comm_data["per_question"]) == 15
    assert comm_data["total_words"] > 0

    # 6. Verify interview intelligence
    intel_res = client.get(f"/api/interviews/{interview_id}/intelligence", headers=headers)
    assert intel_res.status_code == 200
    intel_data = intel_res.json()
    assert intel_data["overall_score"] == 80.0
    assert "ai_summary" in intel_data


# ── 5. End-to-End 20-Question Mock Interview Session ─────────────────────────

def test_complete_20_question_mock_interview():
    email = "user_20_questions@example.com"
    _get_or_create_user(email=email)
    headers = _auth_header(email)

    # 1. Create 20-question interview
    create_res = client.post("/api/interviews", headers=headers, json={
        "job_role": "Software Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": 20,
    })
    assert create_res.status_code == 200
    interview_id = create_res.json()["id"]

    generated_questions = []

    # 2. Sequentially generate, save, and answer all 20 questions
    for seq in range(1, 21):
        gen_res = client.post("/api/ai/generate-question", headers=headers, json={
            "job_role": "Software Developer",
            "interview_type": "Technical Interview",
            "difficulty": "Intermediate",
            "skills": "Python, SQL, REST",
            "interview_id": interview_id,
        })
        assert gen_res.status_code == 200
        gen_data = gen_res.json()
        q_text = gen_data["question"]

        # Ensure no repeat
        assert q_text not in generated_questions, f"Duplicate at sequence {seq}: {q_text}"
        generated_questions.append(q_text)

        # Save question
        save_q_res = client.post(f"/api/interviews/{interview_id}/questions", headers=headers, json={
            "question_text": q_text,
            "question_type": "Technical Interview",
            "difficulty": gen_data.get("difficulty", "Intermediate"),
            "topic": gen_data.get("topic", "Software Development"),
            "sequence_number": seq,
        })
        assert save_q_res.status_code == 200
        qid = save_q_res.json()["id"]

        # Submit answer
        score = 70.0 + (seq % 20)
        ans_res = client.post(f"/api/interviews/{interview_id}/questions/{qid}/answers", headers=headers, json={
            "answer_text": f"This is an elaborate engineering solution for question {seq} addressing architecture and edge cases.",
            "score": score,
            "technical_score": score,
            "communication_score": score,
            "relevance_score": score,
            "completeness_score": score,
            "feedback": f"Good answer for question {seq}.",
        })
        assert ans_res.status_code == 200

    assert len(generated_questions) == 20
    assert len(set(generated_questions)) == 20

    # 3. Complete interview
    comp_res = client.post(f"/api/interviews/{interview_id}/complete", headers=headers, json={"duration": 1800})
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["overall_score"] is not None
    assert comp_data["duration"] == 1800

    # 4. Verify 20 questions in details
    det_res = client.get(f"/api/interviews/{interview_id}/details", headers=headers)
    assert det_res.status_code == 200
    assert len(det_res.json()["questions"]) == 20

    # 5. Verify analytics across all 20 questions
    comm_res = client.get(f"/api/interviews/{interview_id}/communication-analytics", headers=headers)
    assert comm_res.status_code == 200
    assert len(comm_res.json()["per_question"]) == 20


# ── 6. Existing Question Counts (3, 5, 10) Functionality ──────────────────────

@pytest.mark.parametrize("existing_count", [3, 5, 10])
def test_existing_question_counts_work(existing_count):
    email = f"user_existing_{existing_count}@example.com"
    _get_or_create_user(email=email)
    headers = _auth_header(email)

    create_res = client.post("/api/interviews", headers=headers, json={
        "job_role": "AI/ML Engineer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": existing_count,
    })
    assert create_res.status_code == 200
    iid = create_res.json()["id"]

    for seq in range(1, existing_count + 1):
        gen_res = client.post("/api/ai/generate-question", headers=headers, json={
            "job_role": "AI/ML Engineer",
            "interview_type": "Technical Interview",
            "difficulty": "Intermediate",
            "interview_id": iid,
        })
        assert gen_res.status_code == 200
        q_data = gen_res.json()

        save_res = client.post(f"/api/interviews/{iid}/questions", headers=headers, json={
            "question_text": q_data["question"],
            "question_type": "Technical Interview",
            "difficulty": q_data.get("difficulty", "Intermediate"),
            "topic": q_data.get("topic", "AI/ML"),
            "sequence_number": seq,
        })
        qid = save_res.json()["id"]

        client.post(f"/api/interviews/{iid}/questions/{qid}/answers", headers=headers, json={
            "answer_text": "Neural networks use backpropagation to calculate gradient vectors.",
            "score": 85.0,
            "technical_score": 85.0,
            "communication_score": 85.0,
            "relevance_score": 85.0,
            "completeness_score": 85.0,
            "feedback": "Clear explanation.",
        })

    comp_res = client.post(f"/api/interviews/{iid}/complete", headers=headers, json={"duration": existing_count * 120})
    assert comp_res.status_code == 200
    assert comp_res.json()["overall_score"] == 85.0
