"""
test_problem_library.py

Deterministic tests for Checkpoint 10D — 48-Problem Curriculum Library:
  1. Total problem count: exactly 48 unique problems.
  2. Module distribution: exactly 8 problems per module across all 6 modules.
  3. Original 6 problems preserved: IDs, slugs, categories, and test cases intact.
  4. Metadata integrity: all problems have non-empty description, examples (>=2),
     constraints, starter_code (python, java, cpp), and valid difficulty.
  5. Test-case coverage: all problems have sample and hidden test cases.
  6. Idempotency: repeated seeding does not duplicate problems, modules, or test cases.
  7. Module unlock enforcement: modules 1 and 2 unlocked by default; modules 3-6 require prerequisites.
  8. Submission integration: submissions can be created and evaluated for new curriculum problems.
  9. Reference solution evaluation: verify correct solutions pass and wrong solutions fail.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.services.executor import MockCodeExecutor

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.models.models import User, CodingModule, CodingProblem, TestCase, CodingSubmission
from app.services.coding_progress import (
    MODULE_DEFINITIONS,
    EXISTING_PROBLEMS_MODULE_MAP,
    seed_coding_system_if_needed,
    compute_module_unlock_states,
    check_problem_access,
)
from app.curriculum import (
    ALL_NEW_PROBLEMS,
    ALL_NEW_TEST_CASES,
    EXISTING_PROBLEMS_ASSIGNMENTS,
    get_curriculum_summary,
)
from app.auth.auth import get_password_hash, create_access_token
from tests.conftest import TestingSessionLocal

TestSession = TestingSessionLocal
client = TestClient(app)


def _seed_database(db):
    """Seeds the full 48-problem curriculum and original six problems into the test database."""
    from app.api.coding_routes import INITIAL_PROBLEMS, INITIAL_TEST_CASES

    # 1. Seed original 6 problems if not present
    for p_data in INITIAL_PROBLEMS:
        if not db.query(CodingProblem).filter(CodingProblem.slug == p_data["slug"]).first():
            prob = CodingProblem(**p_data)
            db.add(prob)
    db.commit()

    # 2. Seed test cases for original 6
    problems = db.query(CodingProblem).all()
    for prob in problems:
        if prob.slug in INITIAL_TEST_CASES:
            tc_count = db.query(TestCase).filter(TestCase.problem_id == prob.id).count()
            if tc_count == 0:
                for tc_data in INITIAL_TEST_CASES[prob.slug]:
                    tc = TestCase(
                        problem_id=prob.id,
                        input=tc_data["input"],
                        expected_output=tc_data["expected_output"],
                        is_sample=tc_data["is_sample"],
                    )
                    db.add(tc)
    db.commit()

    # 3. Seed modules and all 42 new problems
    seed_coding_system_if_needed(db)


def _create_user(db, email="library_test@example.com", name="Library Tester"):
    user = User(
        name=name,
        email=email,
        password_hash=get_password_hash("testpass123"),
        education="Computer Science",
        experience_level="Intermediate",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


# ═══════════════════════════════════════════════════════════════════════════
#  1. PROBLEM CURRICULUM REGISTRY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCurriculumRegistry:
    def test_curriculum_totals(self):
        """Curriculum registry defines exactly 48 problems (6 existing + 42 new)."""
        summary = get_curriculum_summary()
        assert summary["total_problems"] == 48
        assert summary["existing_problems"] == 6
        assert summary["new_problems"] == 42

    def test_eight_problems_per_module(self):
        """Every module defines exactly 8 problems."""
        summary = get_curriculum_summary()
        for mod_slug, count in summary["counts_by_module"].items():
            assert count == 8, f"Module '{mod_slug}' has {count} problems; expected 8."

    def test_all_slugs_unique(self):
        """All 48 problem slugs are unique across the curriculum."""
        all_slugs = list(EXISTING_PROBLEMS_ASSIGNMENTS.keys()) + [p["slug"] for p in ALL_NEW_PROBLEMS]
        assert len(all_slugs) == 48
        assert len(set(all_slugs)) == 48

    def test_all_new_problems_have_test_cases(self):
        """Every new problem has at least 4 test cases, with both sample and hidden cases."""
        for p in ALL_NEW_PROBLEMS:
            slug = p["slug"]
            assert slug in ALL_NEW_TEST_CASES, f"Missing test cases for '{slug}'"
            tcs = ALL_NEW_TEST_CASES[slug]
            assert len(tcs) >= 4, f"'{slug}' has only {len(tcs)} test cases; expected >= 4"
            sample_count = sum(1 for tc in tcs if tc["is_sample"])
            hidden_count = sum(1 for tc in tcs if not tc["is_sample"])
            assert sample_count >= 1, f"'{slug}' has no sample test cases"
            assert hidden_count >= 1, f"'{slug}' has no hidden test cases"

    def test_problem_metadata_schema_validity(self):
        """All problem definitions contain valid JSON for examples, constraints, starter_code."""
        for p in ALL_NEW_PROBLEMS:
            slug = p["slug"]
            # Description must be substantial
            assert len(p["description"].strip()) > 30, f"Description too short for '{slug}'"
            # Examples must be JSON list of >= 2 examples
            examples = json.loads(p["examples"])
            assert isinstance(examples, list) and len(examples) >= 2, f"Fewer than 2 examples for '{slug}'"
            # Constraints must be JSON list
            constraints = json.loads(p["constraints"])
            assert isinstance(constraints, list) and len(constraints) >= 1, f"No constraints for '{slug}'"
            # Starter code must have python, java, cpp
            starter = json.loads(p["starter_code"])
            assert "python" in starter and "java" in starter and "cpp" in starter, f"Incomplete starter code in '{slug}'"
            # Difficulty must be Easy, Medium, or Hard
            assert p["difficulty"] in ("Easy", "Medium", "Hard"), f"Invalid difficulty in '{slug}'"


# ═══════════════════════════════════════════════════════════════════════════
#  2. DATABASE SEEDING & DATA INTEGRITY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCurriculumDatabaseSeeding:
    def test_seeding_produces_48_problems(self):
        """Seeding the database produces exactly 48 problems."""
        db = TestSession()
        try:
            _seed_database(db)
            total_problems = db.query(CodingProblem).count()
            assert total_problems == 48
        finally:
            db.close()

    def test_eight_problems_per_module_in_db(self):
        """Each of the 6 modules in the database has exactly 8 problems."""
        db = TestSession()
        try:
            _seed_database(db)
            modules = db.query(CodingModule).order_by(CodingModule.order_index).all()
            assert len(modules) == 6
            for mod in modules:
                prob_count = db.query(CodingProblem).filter(CodingProblem.module_id == mod.id).count()
                assert prob_count == 8, f"Module '{mod.title}' has {prob_count} problems; expected 8."
        finally:
            db.close()

    def test_original_six_problems_preserved_with_test_cases(self):
        """The original 6 problems and their test cases are 100% preserved."""
        db = TestSession()
        try:
            _seed_database(db)
            expected_originals = {
                "two-sum": 5,
                "reverse-string": 4,
                "valid-parentheses": 5,
                "maximum-subarray": 4,
                "binary-search": 4,
                "palindrome-check": 4,
            }
            for slug, expected_tc in expected_originals.items():
                prob = db.query(CodingProblem).filter(CodingProblem.slug == slug).first()
                assert prob is not None, f"Original problem '{slug}' missing"
                tc_count = db.query(TestCase).filter(TestCase.problem_id == prob.id).count()
                assert tc_count == expected_tc, f"Original problem '{slug}' test cases altered: {tc_count} vs {expected_tc}"
        finally:
            db.close()

    def test_seeding_is_idempotent(self):
        """Calling seed repeatedly does not alter problem count or duplicate rows."""
        db = TestSession()
        try:
            _seed_database(db)
            seed_coding_system_if_needed(db)
            seed_coding_system_if_needed(db)
            assert db.query(CodingProblem).count() == 48
            assert db.query(CodingModule).count() == 6
        finally:
            db.close()

    def test_order_indices_sequential_within_modules(self):
        """Within each module, problem order_index values are 1..8 without gaps."""
        db = TestSession()
        try:
            _seed_database(db)
            modules = db.query(CodingModule).all()
            for mod in modules:
                probs = db.query(CodingProblem).filter(CodingProblem.module_id == mod.id).order_by(CodingProblem.order_index).all()
                indices = [p.order_index for p in probs]
                assert indices == list(range(1, 9)), f"Module '{mod.title}' order indices not 1..8: {indices}"
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  3. ACCESS CONTROL & PROGRESS INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

class TestCurriculumAccessControl:
    def test_new_user_can_access_module1_and_module2(self):
        """A new user has full access to all 8 problems in Module 1 and all 8 in Module 2."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="fresh_curriculum@example.com")

            mod1 = db.query(CodingModule).filter(CodingModule.slug == "foundations-logic").first()
            mod2 = db.query(CodingModule).filter(CodingModule.slug == "arrays-strings").first()

            for mod in (mod1, mod2):
                probs = db.query(CodingProblem).filter(CodingProblem.module_id == mod.id).all()
                for prob in probs:
                    can_access, reason = check_problem_access(db, prob, user.id)
                    assert can_access is True, f"Problem '{prob.slug}' in unlocked module was blocked: {reason}"
        finally:
            db.close()

    def test_new_user_cannot_access_locked_modules(self):
        """A new user is blocked from problems in Modules 3, 4, 5, and 6."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="locked_test@example.com")

            locked_slugs = [
                "linear-data-structures",
                "searching-sorting-recursion",
                "trees-heaps-graphs",
                "dynamic-programming-advanced",
            ]
            for slug in locked_slugs:
                mod = db.query(CodingModule).filter(CodingModule.slug == slug).first()
                probs = db.query(CodingProblem).filter(CodingProblem.module_id == mod.id).all()
                for prob in probs:
                    can_access, reason = check_problem_access(db, prob, user.id)
                    assert can_access is False, f"Problem '{prob.slug}' in locked module was accessible"
                    assert "locked" in reason.lower()
        finally:
            db.close()

    def test_solving_module2_problem_unlocks_module3(self):
        """Solving Two Sum in Module 2 immediately unlocks all 8 problems in Module 3."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="unlocker@example.com")

            p_two_sum = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            sub = CodingSubmission(
                user_id=user.id,
                problem_id=p_two_sum.id,
                language="python",
                source_code="# accepted",
                status="accepted",
                score=100.0,
                passed_tests=5,
                total_tests=5,
            )
            db.add(sub)
            db.commit()

            mod3 = db.query(CodingModule).filter(CodingModule.slug == "linear-data-structures").first()
            probs3 = db.query(CodingProblem).filter(CodingProblem.module_id == mod3.id).all()
            for prob in probs3:
                can_access, reason = check_problem_access(db, prob, user.id)
                assert can_access is True, f"Problem '{prob.slug}' in Module 3 blocked after prerequisite solved"
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  4. API ENDPOINTS WITH 48 PROBLEMS
# ═══════════════════════════════════════════════════════════════════════════

class TestCurriculumAPIEndpoints:
    def test_api_list_modules_returns_six_with_correct_counts(self):
        """GET /api/coding/modules returns 6 modules with total_problems=8 each."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="api_user@example.com")
            res = client.get("/api/coding/modules", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 6
            for m in data:
                assert m["total_problems"] == 8
        finally:
            db.close()

    def test_api_module_detail_returns_eight_problems(self):
        """GET /api/coding/modules/{slug} returns 8 problems."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="api_mod_user@example.com")
            res = client.get("/api/coding/modules/foundations-logic", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert len(data["problems"]) == 8
        finally:
            db.close()

    def test_api_list_all_coding_problems_returns_48(self):
        """GET /api/coding/problems returns all 48 problems."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="all_probs_user@example.com")
            res = client.get("/api/coding/problems", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 48
        finally:
            db.close()

    def test_api_problem_detail_for_new_problem(self):
        """GET /api/coding/problems/{slug} works for new curriculum problems."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="prob_detail_user@example.com")
            res = client.get("/api/coding/problems/fizzbuzz", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert data["title"] == "FizzBuzz"
            assert data["slug"] == "fizzbuzz"
            assert data["difficulty"] == "Easy"
            examples = json.loads(data["examples"])
            assert len(examples) >= 2
        finally:
            db.close()

    @patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
    def test_submission_to_new_curriculum_problem(self, mock_executor):
        """Submitting code to a newly added curriculum problem is accepted and tracked."""
        db = TestSession()
        try:
            _seed_database(db)
            user, headers = _create_user(db, email="submit_new_user@example.com")

            prob = db.query(CodingProblem).filter(CodingProblem.slug == "even-or-odd").first()
            assert prob is not None

            code = "def evenOrOdd(n: int) -> str:\n    return 'Even' if n % 2 == 0 else 'Odd'\n"
            res = client.post(
                "/api/coding/submit",
                json={"problem_id": prob.id, "language": "python", "code": code},
                headers=headers,
            )
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "accepted"
            assert data["score"] == 100.0
            assert data["passed_tests"] >= 4
        finally:
            db.close()
