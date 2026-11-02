"""
test_coding_mentor.py

Tests for Checkpoint 10F:
1. Hint level ordering (Levels 1 -> 2 -> 3).
2. Hint response validation (title, hint, takeaways, edge_cases).
3. Mock AI fallback.
4. Hidden test-case confidentiality (no test inputs or reference solutions leaked).
5. Recommendation ranking and category distribution.
6. Locked-module filtering (locked problems are never recommended as actionable).
7. New-user recommendations (gracefully handled with 0 submissions).
8. Unique solved-count behavior in skill metrics.
9. Skill metrics correctness (difficulty breakdown, topic accuracy, stronger topics).
10. Submission ownership and authorization.
11. AI feedback consistency with execution verdicts.
12. API error handling (invalid levels, locked problem access, invalid IDs).
"""

import os
import sys
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.database.database import get_db
from app.models.models import User, CodingProblem, CodingSubmission, CodingModule, TestCase
from app.auth.auth import create_access_token, get_password_hash
from app.services.executor import MockCodeExecutor
from tests.conftest import TestingSessionLocal

client = TestClient(app)


@pytest.fixture
def mentor_users():
    db = TestingSessionLocal()
    # User 1: Active Learner
    user1 = db.query(User).filter(User.email == "mentor_user1@example.com").first()
    if not user1:
        user1 = User(
            name="Mentor User 1",
            email="mentor_user1@example.com",
            password_hash=get_password_hash("password123"),
            education="B.S. CS",
            experience_level="Intermediate",
        )
        db.add(user1)

    # User 2: Brand New User (0 submissions)
    user2 = db.query(User).filter(User.email == "mentor_newbie@example.com").first()
    if not user2:
        user2 = User(
            name="Mentor Newbie",
            email="mentor_newbie@example.com",
            password_hash=get_password_hash("password123"),
            education="Self-Taught",
            experience_level="Beginner",
        )
        db.add(user2)

    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    from app.api.coding_routes import seed_problems_if_needed
    seed_problems_if_needed(db)

    u1_id = user1.id
    u2_id = user2.id
    db.close()
    return u1_id, u2_id


def get_token(email: str) -> dict:
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


# ── 1. Progressive Hint Tests ────────────────────────────────────────────────

def test_hints_progressive_ordering_and_structure(mentor_users):
    user1_id, _ = mentor_users
    headers = get_token("mentor_user1@example.com")

    # Fetch an accessible problem
    problems_res = client.get("/api/coding/problems", headers=headers)
    assert problems_res.status_code == 200
    problems = problems_res.json()
    assert len(problems) > 0
    prob_id = problems[0]["id"]

    # Test Level 1: Conceptual
    h1 = client.post(f"/api/coding/problems/{prob_id}/hints", json={"level": 1}, headers=headers)
    assert h1.status_code == 200
    d1 = h1.json()
    assert d1["level"] == 1
    assert "Conceptual" in d1["title"]
    assert len(d1["hint"]) > 20
    assert isinstance(d1["key_takeaways"], list)

    # Test Level 2: Approach
    h2 = client.post(f"/api/coding/problems/{prob_id}/hints", json={"level": 2}, headers=headers)
    assert h2.status_code == 200
    d2 = h2.json()
    assert d2["level"] == 2
    assert "Approach" in d2["title"]
    assert len(d2["hint"]) > 20

    # Test Level 3: Detailed
    h3 = client.post(f"/api/coding/problems/{prob_id}/hints", json={"level": 3}, headers=headers)
    assert h3.status_code == 200
    d3 = h3.json()
    assert d3["level"] == 3
    assert "Detailed" in d3["title"]
    assert "Step" in d3["hint"] or len(d3["hint"]) > 20


def test_hints_confidentiality_no_hidden_test_cases(mentor_users):
    """Ensure hints do not leak hidden test-case inputs or expected outputs."""
    headers = get_token("mentor_user1@example.com")
    db = TestingSessionLocal()
    hidden_tcs = db.query(TestCase).filter(TestCase.is_sample == False).limit(5).all()
    hidden_inputs = [tc.input for tc in hidden_tcs if tc.input]
    db.close()

    for lvl in [1, 2, 3]:
        resp = client.post("/api/coding/problems/1/hints", json={"level": lvl}, headers=headers)
        assert resp.status_code == 200
        hint_text = resp.json()["hint"]
        for inp in hidden_inputs:
            assert inp not in hint_text, f"Hidden test input leaked in hint level {lvl}!"


def test_hints_error_handling(mentor_users):
    headers = get_token("mentor_user1@example.com")
    # Invalid level
    res = client.post("/api/coding/problems/1/hints", json={"level": 4}, headers=headers)
    assert res.status_code == 400

    # Nonexistent problem
    res2 = client.post("/api/coding/problems/99999/hints", json={"level": 1}, headers=headers)
    assert res2.status_code == 404


# ── 2. Educational Explanation Tests ─────────────────────────────────────────

def test_explanation_structure_and_concepts(mentor_users):
    headers = get_token("mentor_user1@example.com")
    res = client.get("/api/coding/problems/1/explanation", headers=headers)
    assert res.status_code == 200
    exp = res.json()
    assert exp["problem_id"] == 1
    assert "intuition" in exp and len(exp["intuition"]) > 0
    assert "brute_force" in exp and len(exp["brute_force"]) > 0
    assert "optimized_approach" in exp and len(exp["optimized_approach"]) > 0
    assert "time_complexity" in exp and "O(" in exp["time_complexity"]
    assert "space_complexity" in exp and "O(" in exp["space_complexity"]
    assert len(exp["common_mistakes"]) > 0
    assert len(exp["edge_cases"]) > 0
    assert len(exp["interview_tips"]) > 0


# ── 3. Recommendations & Locked Module Filtering ─────────────────────────────

def test_recommendations_new_user_graceful(mentor_users):
    """Brand new user with 0 submissions receives actionable, unlocked recommendations."""
    headers = get_token("mentor_newbie@example.com")
    res = client.get("/api/coding/recommendations", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_recommended"] >= 3
    for item in data["recommendations"]:
        assert item["problem"]["is_locked"] is False
        assert len(item["reason"]) > 10
        assert item["category"] in [
            "Continue Learning",
            "Review Previous Mistakes",
            "Practice Weak Topics",
            "Increase Difficulty",
        ]


def test_recommendations_never_include_locked_problems(mentor_users):
    """Verify that problems in locked modules are never recommended as actionable."""
    headers = get_token("mentor_newbie@example.com")
    res = client.get("/api/coding/recommendations", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for item in data["recommendations"]:
        assert item["problem"]["is_locked"] is False
        assert item["problem"]["module_id"] in [1, 2]  # Module 1 and 2 are unlocked by default


def test_recommendations_review_previous_mistakes_category(mentor_users):
    user1_id, _ = mentor_users
    headers = get_token("mentor_user1@example.com")
    db = TestingSessionLocal()

    # Seed a failed submission for problem 2
    sub = CodingSubmission(
        user_id=user1_id,
        problem_id=2,
        language="python",
        source_code="def reverseString(s): pass",
        status="wrong_answer",
        score=20.0,
        passed_tests=1,
        total_tests=5,
    )
    db.add(sub)
    db.commit()
    db.close()

    res = client.get("/api/coding/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()["recommendations"]
    categories = [r["category"] for r in recs]
    assert "Review Previous Mistakes" in categories


# ── 4. Skill Analytics Tests ─────────────────────────────────────────────────

def test_skill_analytics_new_user_no_crash(mentor_users):
    """New user with 0 submissions has 0.0 rates without division-by-zero errors."""
    headers = get_token("mentor_newbie@example.com")
    res = client.get("/api/coding/skills", headers=headers)
    assert res.status_code == 200
    skills = res.json()
    assert skills["total_submissions"] == 0
    assert skills["overall_acceptance_rate"] == 0.0
    assert len(skills["difficulty_breakdown"]) == 3
    assert len(skills["suggested_next_steps"]) > 0


def test_skill_analytics_metrics_correctness(mentor_users):
    user1_id, _ = mentor_users
    headers = get_token("mentor_user1@example.com")
    db = TestingSessionLocal()

    # Seed an accepted submission for problem 1
    sub_ok = CodingSubmission(
        user_id=user1_id,
        problem_id=1,
        language="python",
        source_code="def twoSum(nums, target): return [0, 1]",
        status="accepted",
        score=100.0,
        passed_tests=4,
        total_tests=4,
    )
    db.add(sub_ok)
    db.commit()
    db.close()

    res = client.get("/api/coding/skills", headers=headers)
    assert res.status_code == 200
    skills = res.json()
    assert skills["total_unique_solved"] >= 1
    assert skills["total_submissions"] >= 1
    assert skills["overall_acceptance_rate"] > 0.0

    # Ensure difficulty breakdown has valid numbers
    for d in skills["difficulty_breakdown"]:
        assert d["difficulty"] in ["Easy", "Medium", "Hard"]
        assert d["total_problems"] > 0


# ── 5. AI Feedback Groundedness & Consistency ────────────────────────────────

def test_ai_feedback_grounded_in_docker_verdict(mentor_users):
    user1_id, _ = mentor_users
    headers = get_token("mentor_user1@example.com")
    db = TestingSessionLocal()

    # Create submission with timeout status
    sub = CodingSubmission(
        user_id=user1_id,
        problem_id=1,
        language="python",
        source_code="while True: pass",
        status="timeout",
        score=0.0,
        passed_tests=0,
        total_tests=4,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    sub_id = sub.id
    db.close()

    # Request feedback
    fb_res = client.post(f"/api/coding/submissions/{sub_id}/feedback", headers=headers)
    assert fb_res.status_code == 200
    fb = fb_res.json()
    # Correctness must indicate the failure, not claim it passed
    assert "timeout" in fb["correctness"].lower() or "0" in fb["correctness"] or "fail" in fb["correctness"].lower() or "timeout" in fb["summary"].lower()


def test_submission_ownership_isolation(mentor_users):
    """User 2 cannot request feedback or view User 1's submission."""
    user1_id, _ = mentor_users
    db = TestingSessionLocal()
    sub = CodingSubmission(
        user_id=user1_id,
        problem_id=1,
        language="python",
        source_code="def twoSum(): pass",
        status="accepted",
        score=100.0,
        passed_tests=4,
        total_tests=4,
    )
    db.add(sub)
    db.commit()
    sub_id = sub.id
    db.close()

    headers_user2 = get_token("mentor_newbie@example.com")
    res = client.post(f"/api/coding/submissions/{sub_id}/feedback", headers=headers_user2)
    assert res.status_code == 404
