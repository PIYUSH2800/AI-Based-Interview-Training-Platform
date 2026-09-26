"""
test_interview_intelligence.py

Tests for Checkpoint 7C — Interview Intelligence & Final Evaluation:
  1. Ownership validation (unauthenticated, wrong user)
  2. Deterministic category score arithmetic
  3. Overall score consistency with stored database value
  4. Topic aggregation including null/missing topics
  5. Strength and improvement area detection from actual scores
  6. Practice recommendations linked to weak areas
  7. AI summary fallback (mock works, Gemini failure does not break report)
  8. Incomplete interview (no answers) handled gracefully
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
from tests.conftest import TestingSessionLocal

client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_user(email, name="Intel User"):
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
    uid = user.id
    db.close()
    return uid


def _create_interview(user_id, job_role="Software Developer", interview_type="Technical Interview",
                      difficulty="Intermediate", total_questions=3):
    db = TestingSessionLocal()
    interview = Interview(
        user_id=user_id,
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        mode="Text",
        total_questions=total_questions,
        overall_score=None,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    iid = interview.id
    db.close()
    return iid


def _add_q_and_a(interview_id, seq, q_text, a_text, topic=None,
                 score=80.0, tech=80.0, comm=80.0, rel=80.0, comp=80.0):
    db = TestingSessionLocal()
    q = Question(
        interview_id=interview_id,
        question_text=q_text,
        question_type="Technical Interview",
        difficulty="Intermediate",
        topic=topic,
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
        technical_score=tech,
        communication_score=comm,
        relevance_score=rel,
        completeness_score=comp,
        feedback="Feedback text.",
    )
    db.add(a)
    db.commit()
    db.close()
    return qid


def _token(email):
    return {"Authorization": f"Bearer {create_access_token({'sub': email})}"}


def _complete_interview(interview_id, user_email):
    client.post(f"/api/interviews/{interview_id}/complete", json={"duration": 300},
                headers=_token(user_email))


# ── 1. Ownership / Authentication Tests ──────────────────────────────────────

def test_intelligence_unauthenticated_returns_401():
    resp = client.get("/api/interviews/999/intelligence")
    assert resp.status_code == 401


def test_intelligence_wrong_user_returns_404():
    uid1 = _create_user("intel_owner1@example.com")
    uid2 = _create_user("intel_other1@example.com")
    iid = _create_interview(uid1, job_role="Backend Dev")
    _add_q_and_a(iid, 1, "Question?", "Answer text here.", topic="Python")

    # uid2 should NOT see uid1's interview
    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_other1@example.com"))
    assert resp.status_code == 404


# ── 2. Deterministic Category Arithmetic ─────────────────────────────────────

def test_intelligence_category_scores_match_stored_values():
    """Category averages in intelligence report must match exact arithmetic from DB values."""
    uid = _create_user("intel_cat@example.com")
    iid = _create_interview(uid)

    # Q1: tech=90, comm=70, rel=80, comp=60
    _add_q_and_a(iid, 1, "Q1", "A1", topic="Python", score=75.0, tech=90.0, comm=70.0, rel=80.0, comp=60.0)
    # Q2: tech=70, comm=90, rel=60, comp=80
    _add_q_and_a(iid, 2, "Q2", "A2", topic="SQL",    score=75.0, tech=70.0, comm=90.0, rel=60.0, comp=80.0)
    _complete_interview(iid, "intel_cat@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_cat@example.com"))
    assert resp.status_code == 200
    data = resp.json()

    cat = data["category_scores"]
    assert cat["technical"]     == round((90.0 + 70.0) / 2, 1)   # 80.0
    assert cat["communication"] == round((70.0 + 90.0) / 2, 1)   # 80.0
    assert cat["relevance"]     == round((80.0 + 60.0) / 2, 1)   # 70.0
    assert cat["completeness"]  == round((60.0 + 80.0) / 2, 1)   # 70.0


# ── 3. Overall Score Consistency ─────────────────────────────────────────────

def test_intelligence_overall_score_matches_stored():
    """Overall score in response must match the stored interview.overall_score."""
    uid = _create_user("intel_overall@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Q1", "A1", score=82.0)
    _add_q_and_a(iid, 2, "Q2", "A2", score=74.0)
    _complete_interview(iid, "intel_overall@example.com")

    # Verify stored overall score from complete endpoint
    interview_resp = client.get(f"/api/interviews/{iid}", headers=_token("intel_overall@example.com"))
    stored_overall = interview_resp.json()["overall_score"]

    intel_resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_overall@example.com"))
    assert intel_resp.status_code == 200
    assert intel_resp.json()["overall_score"] == round(stored_overall, 1)


# ── 4. Topic Aggregation ─────────────────────────────────────────────────────

def test_intelligence_topic_aggregation():
    """Questions with same topic should be grouped and averaged correctly."""
    uid = _create_user("intel_topic@example.com")
    iid = _create_interview(uid)
    # Two Python questions
    _add_q_and_a(iid, 1, "Python Q1", "Answer.", topic="Python", score=90.0)
    _add_q_and_a(iid, 2, "Python Q2", "Answer.", topic="Python", score=70.0)
    # One SQL question
    _add_q_and_a(iid, 3, "SQL Q1",    "Answer.", topic="SQL",    score=50.0)
    _complete_interview(iid, "intel_topic@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_topic@example.com"))
    assert resp.status_code == 200
    topics = {t["topic"]: t for t in resp.json()["topic_performance"]}

    assert "Python" in topics
    assert topics["Python"]["question_count"] == 2
    assert topics["Python"]["average_score"]  == 80.0

    assert "SQL" in topics
    assert topics["SQL"]["question_count"]   == 1
    assert topics["SQL"]["average_score"]    == 50.0
    assert topics["SQL"]["coverage_status"]  == "Needs Practice"


def test_intelligence_null_topic_falls_back_to_general():
    """Questions with no topic set should be grouped under 'General'."""
    uid = _create_user("intel_notopic@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Generic Q", "Answer.", topic=None, score=78.0)
    _complete_interview(iid, "intel_notopic@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_notopic@example.com"))
    assert resp.status_code == 200
    topics = {t["topic"]: t for t in resp.json()["topic_performance"]}
    assert "General" in topics


# ── 5. Strength Detection ─────────────────────────────────────────────────────

def test_intelligence_strengths_detected_from_high_scores():
    uid = _create_user("intel_strong@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Q1", "A1", score=88.0, tech=88.0, comm=88.0, rel=88.0, comp=88.0)
    _complete_interview(iid, "intel_strong@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_strong@example.com"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["strengths"]) > 0


def test_intelligence_no_false_strengths_for_low_scores():
    uid = _create_user("intel_weak@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Q1", "A1", score=50.0, tech=50.0, comm=50.0, rel=50.0, comp=50.0)
    _complete_interview(iid, "intel_weak@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_weak@example.com"))
    assert resp.status_code == 200
    data = resp.json()
    # With all scores at 50, no category should appear as a strength
    cat_strength_keywords = ["technical knowledge", "communication", "relevant", "complete"]
    for s in data["strengths"]:
        for kw in cat_strength_keywords:
            assert kw not in s.lower(), f"False strength detected: '{s}'"


# ── 6. Improvement Areas & Recommendations ───────────────────────────────────

def test_intelligence_improvement_areas_for_weak_categories():
    uid = _create_user("intel_improve@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Q1", "A1", score=55.0, tech=55.0, comm=55.0, rel=55.0, comp=55.0)
    _complete_interview(iid, "intel_improve@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_improve@example.com"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["improvement_areas"]) > 0
    assert len(data["practice_recommendations"]) > 0


def test_intelligence_recommendations_for_weak_topic():
    uid = _create_user("intel_recs@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Docker Q", "A1", topic="Docker", score=50.0,
                 tech=50.0, comm=50.0, rel=50.0, comp=50.0)
    _complete_interview(iid, "intel_recs@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_recs@example.com"))
    assert resp.status_code == 200
    recs_text = " ".join(resp.json()["practice_recommendations"]).lower()
    assert "docker" in recs_text


# ── 7. AI Summary ─────────────────────────────────────────────────────────────

def test_intelligence_ai_summary_present_in_response():
    """Mock AI summary must be returned (never empty when fallback is available)."""
    uid = _create_user("intel_aisummary@example.com")
    iid = _create_interview(uid)
    _add_q_and_a(iid, 1, "Q1", "A1", score=75.0)
    _complete_interview(iid, "intel_aisummary@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_aisummary@example.com"))
    assert resp.status_code == 200
    summary = resp.json()["ai_summary"]
    assert isinstance(summary, str)
    assert len(summary) > 20  # Non-trivial summary


# ── 8. Incomplete Interview (No Answers) ──────────────────────────────────────

def test_intelligence_no_answers_handled_gracefully():
    uid = _create_user("intel_empty@example.com")
    iid = _create_interview(uid)
    # Add question without answer
    db = TestingSessionLocal()
    q = Question(
        interview_id=iid,
        question_text="Unanswered Q",
        question_type="Technical Interview",
        difficulty="Intermediate",
        sequence_number=1,
    )
    db.add(q)
    db.commit()
    db.close()

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_empty@example.com"))
    assert resp.status_code == 200
    data = resp.json()
    # Scores should be 0 or defaults; should not crash
    assert data["overall_score"] is not None
    assert data["category_scores"]["technical"] == 0.0
    assert isinstance(data["topic_performance"], list)
    assert isinstance(data["strengths"], list)
    assert isinstance(data["improvement_areas"], list)
    assert isinstance(data["practice_recommendations"], list)


# ── 9. Response Schema Completeness ───────────────────────────────────────────

def test_intelligence_response_has_all_required_fields():
    uid = _create_user("intel_schema@example.com")
    iid = _create_interview(uid, job_role="Data Scientist", interview_type="Technical Interview")
    _add_q_and_a(iid, 1, "Q1", "A1", score=75.0, topic="Machine Learning")
    _complete_interview(iid, "intel_schema@example.com")

    resp = client.get(f"/api/interviews/{iid}/intelligence", headers=_token("intel_schema@example.com"))
    assert resp.status_code == 200
    data = resp.json()

    required_fields = [
        "interview_id", "job_role", "interview_type", "difficulty",
        "overall_score", "category_scores", "topic_performance",
        "strengths", "improvement_areas", "practice_recommendations", "ai_summary",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    cat_fields = ["technical", "communication", "relevance", "completeness"]
    for field in cat_fields:
        assert field in data["category_scores"], f"Missing category_scores field: {field}"

    assert data["job_role"] == "Data Scientist"
    assert data["interview_type"] == "Technical Interview"
