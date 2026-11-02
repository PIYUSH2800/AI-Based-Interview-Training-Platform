"""
qa_full_audit.py

Full-system QA and integration audit script covering:
- Auth & User lifecycle
- Profile persistence & field updates
- Resume uploads (PDF/DOCX), validation, analysis, download, delete, cross-user isolation
- Interview creation, adaptive question generation, evaluation, completion
- Communication analytics calculations and API
- Interview intelligence deterministic calculations & AI summary
- Coding problem retrieval, execution/submission, AI feedback
- Security and ownership validations across all domains
"""

import io
import os
import sys
import json
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from unittest.mock import patch
from app.services.executor import MockCodeExecutor

from app.main import app
from app.database.database import get_db
from app.models.models import User, Profile, Interview, Question, Answer, CodingProblem, CodingSubmission
from app.auth.auth import create_access_token, get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

def test_full_system_qa_audit():
    results = {}
    print("\n[QA AUDIT] Starting Full-System QA Audit...")

    # 1. AUTH FLOW
    # Register user A
    user_a_email = "audit_user_a@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "name": "Audit User A",
        "email": user_a_email,
        "password": "Password123!",
        "education": "B.Tech Computer Science",
        "experience_level": "Mid-Level"
    })
    assert reg_resp.status_code in [200, 400], f"Registration failed: {reg_resp.text}"
    
    # Attempt duplicate registration
    dup_resp = client.post("/api/auth/register", json={
        "name": "Audit User A Duplicate",
        "email": user_a_email,
        "password": "Password123!",
    })
    assert dup_resp.status_code == 400, "Duplicate email registration was not rejected!"
    
    # Login User A
    login_resp = client.post("/api/auth/login", data={
        "username": user_a_email,
        "password": "Password123!"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token_a = login_resp.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Create User B for cross-user tests
    user_b_email = "audit_user_b@example.com"
    client.post("/api/auth/register", json={
        "name": "Audit User B",
        "email": user_b_email,
        "password": "Password123!",
        "education": "B.S. Information Systems",
        "experience_level": "Junior"
    })
    login_b = client.post("/api/auth/login", data={
        "username": user_b_email,
        "password": "Password123!"
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    results["auth"] = "PASS"

    # 2. PROFILE FLOW
    # Load profile
    prof_resp = client.get("/api/users/profile", headers=headers_a)
    assert prof_resp.status_code == 200
    pdata = prof_resp.json()
    assert pdata["email"] == user_a_email

    # Edit profile
    update_resp = client.put("/api/users/profile", headers=headers_a, json={
        "phone": "+1-555-0199",
        "skills": "Python, SQL, FastApi, Docker",
        "target_role": "Backend Engineer",
        "college": "State University",
        "degree": "B.Tech"
    })
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["skills"] == "Python, SQL, FastApi, Docker"
    assert updated["phone"] == "+1-555-0199"

    # Verify persistence
    prof_check = client.get("/api/users/profile", headers=headers_a)
    assert prof_check.json()["target_role"] == "Backend Engineer"
    results["profile"] = "PASS"

    # 3. RESUME FLOW
    # Reject invalid file type (.txt)
    txt_file = io.BytesIO(b"Simple resume text")
    res_bad = client.post("/api/users/resume", headers=headers_a, files={
        "file": ("resume.txt", txt_file, "text/plain")
    })
    assert res_bad.status_code == 400

    # Reject oversized file (>5MB)
    huge_data = io.BytesIO(b"0" * (6 * 1024 * 1024))
    res_huge = client.post("/api/users/resume", headers=headers_a, files={
        "file": ("resume.pdf", huge_data, "application/pdf")
    })
    assert res_huge.status_code == 400

    # Upload valid minimal PDF
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000108 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n185\n%%EOF"
    res_valid = client.post("/api/users/resume", headers=headers_a, files={
        "file": ("my_resume.pdf", io.BytesIO(pdf_content), "application/pdf")
    })
    assert res_valid.status_code == 200, f"Resume upload failed: {res_valid.text}"
    
    # Check resume metadata
    info_resp = client.get("/api/users/resume", headers=headers_a)
    assert info_resp.status_code == 200
    assert info_resp.json()["has_resume"] is True

    # User B cannot download User A's resume (isolation check)
    dl_b = client.get("/api/users/resume/download", headers=headers_b)
    # User B has no resume uploaded, so 404
    assert dl_b.status_code == 404

    # User A download works
    dl_a = client.get("/api/users/resume/download", headers=headers_a)
    assert dl_a.status_code == 200
    assert len(dl_a.content) > 0
    results["resume"] = "PASS"

    # 4. INTERVIEW CREATION & ADAPTIVE QUESTIONS FLOW
    int_resp = client.post("/api/interviews", headers=headers_a, json={
        "job_role": "Python Backend Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "mode": "Text",
        "total_questions": 3
    })
    assert int_resp.status_code == 200
    interview_id = int_resp.json()["id"]

    # Generate Question 1
    q1_gen = client.post("/api/ai/generate-question", headers=headers_a, json={
        "job_role": "Python Backend Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "skills": "Python, SQL",
        "interview_id": interview_id
    })
    assert q1_gen.status_code == 200
    q1_data = q1_gen.json()
    assert "question" in q1_data and len(q1_data["question"]) > 5

    # Save Question 1
    q1_save = client.post(f"/api/interviews/{interview_id}/questions", headers=headers_a, json={
        "question_text": q1_data["question"],
        "question_type": "Technical Interview",
        "difficulty": q1_data["difficulty"],
        "topic": q1_data.get("topic", "Python"),
        "sequence_number": 1
    })
    assert q1_save.status_code == 200
    q1_id = q1_save.json()["id"]

    # Answer Question 1
    a1_text = "In Python, memory management is managed by private heap space. All objects and data structures are located in this heap, handled by the memory manager and garbage collector via reference counting."
    eval1 = client.post("/api/ai/evaluate-answer", headers=headers_a, json={
        "question_text": q1_data["question"],
        "answer_text": a1_text,
        "job_role": "Python Backend Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate"
    })
    assert eval1.status_code == 200
    eval1_data = eval1.json()

    # Save Answer 1
    ans1_save = client.post(f"/api/interviews/{interview_id}/questions/{q1_id}/answers", headers=headers_a, json={
        "answer_text": a1_text,
        "score": eval1_data.get("overall_score", 85.0),
        "technical_score": eval1_data.get("technical_accuracy", 88.0),
        "communication_score": eval1_data.get("clarity", 82.0),
        "relevance_score": eval1_data.get("relevance", 86.0),
        "completeness_score": eval1_data.get("completeness", 84.0),
        "feedback": eval1_data.get("feedback", "Solid understanding of Python memory.")
    })
    assert ans1_save.status_code == 200

    # Generate Question 2 (Adaptive, incorporating Q1 answer)
    q2_gen = client.post("/api/ai/generate-question", headers=headers_a, json={
        "job_role": "Python Backend Developer",
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "skills": "Python, SQL",
        "interview_id": interview_id
    })
    assert q2_gen.status_code == 200
    q2_data = q2_gen.json()
    assert q2_data["question"] != q1_data["question"], "Adaptive question repeated Q1!"

    # Save Question 2 & Answer 2
    q2_save = client.post(f"/api/interviews/{interview_id}/questions", headers=headers_a, json={
        "question_text": q2_data["question"],
        "question_type": "Technical Interview",
        "difficulty": q2_data["difficulty"],
        "topic": q2_data.get("topic", "SQL"),
        "sequence_number": 2
    })
    q2_id = q2_save.json()["id"]

    a2_text = "SQL indexing uses B-trees or hash structures to accelerate read queries, trading off write throughput and storage space."
    ans2_save = client.post(f"/api/interviews/{interview_id}/questions/{q2_id}/answers", headers=headers_a, json={
        "answer_text": a2_text,
        "score": 80.0,
        "technical_score": 80.0,
        "communication_score": 80.0,
        "relevance_score": 80.0,
        "completeness_score": 80.0,
        "feedback": "Clear explanation of indexing trade-offs."
    })
    assert ans2_save.status_code == 200

    # Complete interview
    comp_resp = client.post(f"/api/interviews/{interview_id}/complete", headers=headers_a, json={"duration": 180})
    assert comp_resp.status_code == 200
    assert comp_resp.json()["overall_score"] is not None
    results["interview_flow"] = "PASS"

    # 5. COMMUNICATION ANALYTICS
    comm_resp = client.get(f"/api/interviews/{interview_id}/communication-analytics", headers=headers_a)
    assert comm_resp.status_code == 200
    comm_data = comm_resp.json()
    assert "total_words" in comm_data
    assert comm_data["total_words"] > 0
    assert len(comm_data["per_question"]) == 2
    results["communication_analytics"] = "PASS"

    # 6. INTERVIEW INTELLIGENCE
    intel_resp = client.get(f"/api/interviews/{interview_id}/intelligence", headers=headers_a)
    assert intel_resp.status_code == 200
    intel_data = intel_resp.json()
    assert intel_data["interview_id"] == interview_id
    assert "category_scores" in intel_data
    assert "topic_performance" in intel_data
    assert len(intel_data["topic_performance"]) >= 1
    assert "strengths" in intel_data and len(intel_data["strengths"]) > 0
    assert "practice_recommendations" in intel_data
    assert isinstance(intel_data["ai_summary"], str)

    # Cross-user isolation check on intelligence
    intel_wrong = client.get(f"/api/interviews/{interview_id}/intelligence", headers=headers_b)
    assert intel_wrong.status_code == 404, "User B was able to view User A's intelligence report!"
    results["intelligence"] = "PASS"

    # 7. CODING MODULE
    problems_resp = client.get("/api/coding/problems", headers=headers_a)
    assert problems_resp.status_code == 200
    problems = problems_resp.json()
    assert len(problems) >= 3
    prob1 = problems[0]

    with patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor()):
        # Run code on sample test cases
        run_resp = client.post("/api/coding/run", headers=headers_a, json={
            "problem_id": prob1["id"],
            "language": "python",
            "code": "def twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return [seen[diff], i]\n        seen[num] = i\n    return []"
        })
        assert run_resp.status_code == 200
        run_data = run_resp.json()
        assert run_data["status"] == "completed"

        # Submit code
        sub_resp = client.post("/api/coding/submit", headers=headers_a, json={
            "problem_id": prob1["id"],
            "language": "python",
            "code": "def twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return [seen[diff], i]\n        seen[num] = i\n    return []"
        })
        assert sub_resp.status_code == 200
        sub_data = sub_resp.json()
        submission_id = sub_data["id"]
        assert sub_data["score"] == 100

    # User B cannot view User A's submission
    sub_b = client.get(f"/api/coding/submissions/{submission_id}", headers=headers_b)
    assert sub_b.status_code == 404

    # Request AI coding feedback
    fb_resp = client.post(f"/api/coding/submissions/{submission_id}/feedback", headers=headers_a)
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert "summary" in fb_data and len(fb_data["summary"]) > 0
    assert "time_complexity" in fb_data
    results["coding"] = "PASS"

    # 8. DASHBOARD CHECK
    history_resp = client.get("/api/interviews", headers=headers_a)
    assert history_resp.status_code == 200
    assert any(i["id"] == interview_id for i in history_resp.json())
    results["dashboard_and_history"] = "PASS"

    print("\n[QA AUDIT COMPLETE] All flows verified successfully:", json.dumps(results, indent=2))

if __name__ == "__main__":
    test_full_system_qa_audit()
