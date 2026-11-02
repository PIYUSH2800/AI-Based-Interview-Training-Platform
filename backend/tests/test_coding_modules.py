"""
test_coding_modules.py

Deterministic tests for the Checkpoint 10C progressive coding learning system:
  - Module seeding and idempotency
  - Module listing and detail endpoints
  - User progress tracking (unique solved only)
  - Module unlock rules and prerequisites
  - Problem access control (locked modules, reattempt bypass)
  - Data preservation (existing 6 problems mapped correctly)
"""

import os
import sys

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.models import (
    User,
    CodingModule,
    CodingProblem,
    TestCase,
    CodingSubmission,
)
from app.services.coding_progress import (
    MODULE_DEFINITIONS,
    EXISTING_PROBLEMS_MODULE_MAP,
    seed_coding_system_if_needed,
    get_user_unique_solved_problem_ids,
    get_user_solved_problems_by_module,
    compute_module_unlock_states,
    check_problem_access,
)
from app.auth.auth import get_password_hash, create_access_token


# ── Database Session and Client ──────────────────────────────────────────────

from tests.conftest import TestingSessionLocal

TestSession = TestingSessionLocal
client = TestClient(app)


def _create_user(db, email="test@modules.com", name="Module User"):
    """Helper to create a test user and return (user, auth_headers)."""
    user = User(
        name=name,
        email=email,
        password_hash=get_password_hash("testpass123"),
        education="CS",
        experience_level="Mid",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def _seed_original_six(db):
    """Seeds the original 6 coding problems with test cases and maps them to modules."""
    from app.api.coding_routes import INITIAL_PROBLEMS, INITIAL_TEST_CASES

    for p_data in INITIAL_PROBLEMS:
        prob = CodingProblem(**p_data)
        db.add(prob)
    db.commit()

    problems = db.query(CodingProblem).all()
    for prob in problems:
        if prob.slug in INITIAL_TEST_CASES:
            for tc_data in INITIAL_TEST_CASES[prob.slug]:
                tc = TestCase(
                    problem_id=prob.id,
                    input=tc_data["input"],
                    expected_output=tc_data["expected_output"],
                    is_sample=tc_data["is_sample"],
                )
                db.add(tc)
    db.commit()

    seed_coding_system_if_needed(db)


def _submit_accepted(db, user_id, problem_id, lang="python"):
    """Create an accepted submission for a user on a problem."""
    sub = CodingSubmission(
        user_id=user_id,
        problem_id=problem_id,
        language=lang,
        source_code="# accepted solution",
        status="accepted",
        score=100.0,
        passed_tests=4,
        total_tests=4,
        execution_time_ms=10.0,
    )
    db.add(sub)
    db.commit()
    return sub


def _submit_wrong(db, user_id, problem_id, lang="python"):
    """Create a wrong_answer submission for a user on a problem."""
    sub = CodingSubmission(
        user_id=user_id,
        problem_id=problem_id,
        language=lang,
        source_code="# wrong solution",
        status="wrong_answer",
        score=25.0,
        passed_tests=1,
        total_tests=4,
        execution_time_ms=5.0,
    )
    db.add(sub)
    db.commit()
    return sub


# ═══════════════════════════════════════════════════════════════════════════
#  1. MODULE DEFINITIONS AND SEEDING
# ═══════════════════════════════════════════════════════════════════════════

class TestModuleDefinitions:
    def test_six_modules_defined(self):
        """Exactly 6 progressive modules are defined."""
        assert len(MODULE_DEFINITIONS) == 6

    def test_modules_have_unique_slugs(self):
        """All module slugs are unique."""
        slugs = [m["slug"] for m in MODULE_DEFINITIONS]
        assert len(slugs) == len(set(slugs))

    def test_modules_have_sequential_order_indices(self):
        """Module order_index values are 1..6."""
        indices = sorted([m["order_index"] for m in MODULE_DEFINITIONS])
        assert indices == [1, 2, 3, 4, 5, 6]

    def test_first_two_modules_have_no_prerequisite(self):
        """Modules 1 (Foundations) and 2 (Arrays & Strings) are unlocked by default."""
        for m in MODULE_DEFINITIONS:
            if m["order_index"] in (1, 2):
                assert m["prerequisite_slug"] is None
                assert m["required_prerequisite_count"] == 0

    def test_existing_six_problems_mapped(self):
        """All 6 original problem slugs are accounted for in EXISTING_PROBLEMS_MODULE_MAP."""
        expected_slugs = {
            "palindrome-check", "reverse-string", "two-sum",
            "valid-parentheses", "binary-search", "maximum-subarray",
        }
        assert set(EXISTING_PROBLEMS_MODULE_MAP.keys()) == expected_slugs


class TestModuleSeeding:
    def test_seeding_creates_modules(self):
        """seed_coding_system_if_needed creates all 6 module rows."""
        db = TestSession()
        try:
            seed_coding_system_if_needed(db)
            modules = db.query(CodingModule).all()
            assert len(modules) == 6
        finally:
            db.close()

    def test_seeding_is_idempotent(self):
        """Calling seed twice does not duplicate modules."""
        db = TestSession()
        try:
            seed_coding_system_if_needed(db)
            seed_coding_system_if_needed(db)
            modules = db.query(CodingModule).all()
            assert len(modules) == 6
        finally:
            db.close()

    def test_seeding_maps_original_six_problems(self):
        """After seeding with the 6 problems, each is mapped to the correct module."""
        db = TestSession()
        try:
            _seed_original_six(db)
            for slug, mapping in EXISTING_PROBLEMS_MODULE_MAP.items():
                prob = db.query(CodingProblem).filter(CodingProblem.slug == slug).first()
                assert prob is not None, f"Problem '{slug}' not found"
                mod = db.query(CodingModule).filter(CodingModule.slug == mapping["module_slug"]).first()
                assert prob.module_id == mod.id, f"Problem '{slug}' not mapped to '{mapping['module_slug']}'"
                assert prob.order_index == mapping["order_index"]
        finally:
            db.close()

    def test_seeding_preserves_existing_problem_ids(self):
        """Seeding does not alter the auto-increment IDs of the original 6 problems."""
        db = TestSession()
        try:
            _seed_original_six(db)
            problems = db.query(CodingProblem).order_by(CodingProblem.id).all()
            ids = [p.id for p in problems]
            assert ids[:6] == [1, 2, 3, 4, 5, 6]
        finally:
            db.close()

    def test_seeding_preserves_existing_test_cases(self):
        """Seeding modules does not delete or duplicate test cases."""
        db = TestSession()
        try:
            _seed_original_six(db)
            tc_count_before = db.query(TestCase).count()
            seed_coding_system_if_needed(db)
            tc_count_after = db.query(TestCase).count()
            assert tc_count_after == tc_count_before
            assert tc_count_after > 0
        finally:
            db.close()

    def test_module_prerequisite_links(self):
        """Modules with prerequisites have correct prerequisite_module_id set."""
        db = TestSession()
        try:
            seed_coding_system_if_needed(db)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            # Linear Data Structures → prerequisite: Arrays & Strings
            assert mods["linear-data-structures"].prerequisite_module_id == mods["arrays-strings"].id
            # Searching, Sorting & Recursion → prerequisite: Linear Data Structures
            assert mods["searching-sorting-recursion"].prerequisite_module_id == mods["linear-data-structures"].id
            # Trees, Heaps & Graphs → prerequisite: Searching, Sorting & Recursion
            assert mods["trees-heaps-graphs"].prerequisite_module_id == mods["searching-sorting-recursion"].id
            # DP & Advanced → prerequisite: Searching, Sorting & Recursion
            assert mods["dynamic-programming-advanced"].prerequisite_module_id == mods["searching-sorting-recursion"].id
            # First two have no prerequisite
            assert mods["foundations-logic"].prerequisite_module_id is None
            assert mods["arrays-strings"].prerequisite_module_id is None
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  2. USER PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════════

class TestUserProgress:
    def test_no_solved_when_no_submissions(self):
        """A user with no submissions has empty solved set."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            solved = get_user_unique_solved_problem_ids(db, user.id)
            assert solved == set()
        finally:
            db.close()

    def test_accepted_submission_counted(self):
        """An accepted submission adds the problem_id to the solved set."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)
            prob = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, prob.id)

            solved = get_user_unique_solved_problem_ids(db, user.id)
            assert prob.id in solved
        finally:
            db.close()

    def test_wrong_answer_not_counted(self):
        """A wrong_answer submission does NOT add to the solved set."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)
            prob = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_wrong(db, user.id, prob.id)

            solved = get_user_unique_solved_problem_ids(db, user.id)
            assert prob.id not in solved
        finally:
            db.close()

    def test_duplicate_accepted_counted_once(self):
        """Multiple accepted submissions for the same problem count as 1 unique solve."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)
            prob = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, prob.id)
            _submit_accepted(db, user.id, prob.id)
            _submit_accepted(db, user.id, prob.id)

            solved = get_user_unique_solved_problem_ids(db, user.id)
            assert len(solved) == 1
        finally:
            db.close()

    def test_solved_by_module_correct(self):
        """get_user_solved_problems_by_module groups correctly."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            palindrome = db.query(CodingProblem).filter(CodingProblem.slug == "palindrome-check").first()
            reverse_str = db.query(CodingProblem).filter(CodingProblem.slug == "reverse-string").first()
            two_sum = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()

            _submit_accepted(db, user.id, palindrome.id)
            _submit_accepted(db, user.id, reverse_str.id)
            _submit_accepted(db, user.id, two_sum.id)

            by_mod = get_user_solved_problems_by_module(db, user.id)

            arrays_mod = db.query(CodingModule).filter(CodingModule.slug == "arrays-strings").first()
            assert len(by_mod.get(arrays_mod.id, set())) == 3  # palindrome + reverse + two_sum
        finally:
            db.close()

    def test_anonymous_user_has_no_progress(self):
        """Passing user_id=None returns empty results."""
        db = TestSession()
        try:
            solved = get_user_unique_solved_problem_ids(db, None)
            assert solved == set()
            by_mod = get_user_solved_problems_by_module(db, None)
            assert by_mod == {}
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  3. MODULE UNLOCK RULES
# ═══════════════════════════════════════════════════════════════════════════

class TestUnlockRules:
    def test_default_modules_unlocked_for_new_user(self):
        """Modules 1 and 2 are unlocked by default; 3–6 are locked."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            states = compute_module_unlock_states(db, user.id)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            # Foundations & Logic — unlocked
            assert states[mods["foundations-logic"].id]["is_unlocked"] is True
            # Arrays & Strings — unlocked
            assert states[mods["arrays-strings"].id]["is_unlocked"] is True
            # Linear Data Structures — locked (requires 1 in arrays-strings)
            assert states[mods["linear-data-structures"].id]["is_unlocked"] is False
            # Searching — locked
            assert states[mods["searching-sorting-recursion"].id]["is_unlocked"] is False
        finally:
            db.close()

    def test_solving_prerequisite_unlocks_module(self):
        """Solving 1 problem in 'Arrays & Strings' unlocks 'Linear Data Structures'."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            two_sum = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, two_sum.id)

            states = compute_module_unlock_states(db, user.id)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            assert states[mods["linear-data-structures"].id]["is_unlocked"] is True
        finally:
            db.close()

    def test_locked_module_shows_unlock_requirement(self):
        """A locked module's state includes a human-readable unlock requirement."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            states = compute_module_unlock_states(db, user.id)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            lds_state = states[mods["linear-data-structures"].id]
            assert "Solve" in lds_state["unlock_requirement"]
            assert "Arrays & Strings" in lds_state["unlock_requirement"]
        finally:
            db.close()

    def test_chain_unlock_three_levels(self):
        """Solving through the prerequisite chain unlocks modules sequentially."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            # Solve in arrays-strings → unlocks linear-data-structures
            two_sum = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, two_sum.id)

            # Solve in linear-data-structures → unlocks searching-sorting-recursion
            valid_parens = db.query(CodingProblem).filter(CodingProblem.slug == "valid-parentheses").first()
            _submit_accepted(db, user.id, valid_parens.id)

            states = compute_module_unlock_states(db, user.id)
            assert states[mods["searching-sorting-recursion"].id]["is_unlocked"] is True

            # Trees and DP still locked (need 1 in searching-sorting-recursion)
            assert states[mods["trees-heaps-graphs"].id]["is_unlocked"] is False
            assert states[mods["dynamic-programming-advanced"].id]["is_unlocked"] is False

            # Solve binary-search (in searching-sorting-recursion) → unlocks both trees and DP
            binary_search = db.query(CodingProblem).filter(CodingProblem.slug == "binary-search").first()
            _submit_accepted(db, user.id, binary_search.id)

            states = compute_module_unlock_states(db, user.id)
            assert states[mods["trees-heaps-graphs"].id]["is_unlocked"] is True
            assert states[mods["dynamic-programming-advanced"].id]["is_unlocked"] is True
        finally:
            db.close()

    def test_unlock_states_for_anonymous(self):
        """Anonymous users see modules 1 and 2 unlocked, rest locked."""
        db = TestSession()
        try:
            _seed_original_six(db)
            states = compute_module_unlock_states(db, None)
            mods = {m.slug: m for m in db.query(CodingModule).all()}

            assert states[mods["foundations-logic"].id]["is_unlocked"] is True
            assert states[mods["arrays-strings"].id]["is_unlocked"] is True
            assert states[mods["linear-data-structures"].id]["is_unlocked"] is False
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  4. PROBLEM ACCESS CONTROL
# ═══════════════════════════════════════════════════════════════════════════

class TestProblemAccess:
    def test_unlocked_module_problem_accessible(self):
        """A problem in an unlocked module is accessible."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            palindrome = db.query(CodingProblem).filter(CodingProblem.slug == "palindrome-check").first()
            accessible, reason = check_problem_access(db, palindrome, user.id)
            assert accessible is True
            assert reason is None
        finally:
            db.close()

    def test_locked_module_problem_blocked(self):
        """A problem in a locked module is NOT accessible."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            valid_parens = db.query(CodingProblem).filter(CodingProblem.slug == "valid-parentheses").first()
            accessible, reason = check_problem_access(db, valid_parens, user.id)
            assert accessible is False
            assert "locked" in reason.lower()
        finally:
            db.close()

    def test_solved_problem_always_accessible_even_if_locked(self):
        """A previously solved problem can always be reattempted, even if the module is locked."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            # Manually force a solve on a problem in a locked module
            valid_parens = db.query(CodingProblem).filter(CodingProblem.slug == "valid-parentheses").first()
            _submit_accepted(db, user.id, valid_parens.id)

            accessible, reason = check_problem_access(db, valid_parens, user.id)
            assert accessible is True
        finally:
            db.close()

    def test_unassigned_module_problem_accessible(self):
        """A problem with no module_id is always accessible."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            # Create a problem without a module
            prob = CodingProblem(
                title="Orphan Problem",
                slug="orphan-problem",
                difficulty="Easy",
                category="Misc",
                description="Test",
                examples="[]",
                constraints="[]",
                starter_code="{}",
                supported_languages='["python"]',
            )
            db.add(prob)
            db.commit()

            accessible, reason = check_problem_access(db, prob, user.id)
            assert accessible is True
        finally:
            db.close()

    def test_none_problem_returns_not_found(self):
        """Passing None for problem returns (False, 'Problem not found.')."""
        db = TestSession()
        try:
            accessible, reason = check_problem_access(db, None, 1)
            assert accessible is False
            assert "not found" in reason.lower()
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  5. MODULE API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

class TestModuleAPI:
    def test_list_modules_returns_six(self):
        """GET /api/coding/modules returns all 6 modules."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6

    def test_list_modules_ordered_by_order_index(self):
        """Modules are returned sorted by order_index."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules", headers=headers)
        data = resp.json()
        indices = [m["order_index"] for m in data]
        assert indices == sorted(indices)

    def test_list_modules_includes_unlock_state(self):
        """Each module in the list has is_unlocked and unlock_requirement fields."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules", headers=headers)
        data = resp.json()
        for m in data:
            assert "is_unlocked" in m
            assert "unlock_requirement" in m

    def test_list_modules_unauthenticated(self):
        """Unauthenticated users can still list modules (get_current_user_optional)."""
        db = TestSession()
        try:
            _seed_original_six(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6

    def test_module_detail_returns_problems(self):
        """GET /api/coding/modules/{slug} returns module with its problems."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules/foundations-logic", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "foundations-logic"
        assert len(data["problems"]) == 8

    def test_module_detail_problem_solved_status(self):
        """Problems show is_solved=True after user solves them."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
            palindrome = db.query(CodingProblem).filter(CodingProblem.slug == "palindrome-check").first()
            _submit_accepted(db, user.id, palindrome.id)
        finally:
            db.close()

        resp = client.get("/api/coding/modules/arrays-strings", headers=headers)
        data = resp.json()
        for p in data["problems"]:
            if p["slug"] == "palindrome-check":
                assert p["is_solved"] is True
            elif p["slug"] == "reverse-string":
                assert p["is_solved"] is False

    def test_module_detail_404_for_unknown_slug(self):
        """Requesting a non-existent module slug returns 404."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/modules/nonexistent", headers=headers)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
#  6. PROGRESS API ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

class TestProgressAPI:
    def test_progress_requires_auth(self):
        """GET /api/coding/progress without auth returns 401."""
        resp = client.get("/api/coding/progress")
        assert resp.status_code == 401

    def test_progress_fresh_user(self):
        """A fresh user has 0 solved, 6 total problems, 2 unlocked modules."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/progress", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_unique_solved"] == 0
        assert data["total_problems"] == 48  # 48 problems assigned to modules
        assert data["overall_progress_percent"] == 0.0
        assert data["unlocked_modules_count"] == 2  # Foundations + Arrays
        assert data["total_modules_count"] == 6

    def test_progress_after_solving_problems(self):
        """Progress reflects unique solved count after accepted submissions."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
            palindrome = db.query(CodingProblem).filter(CodingProblem.slug == "palindrome-check").first()
            two_sum = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, palindrome.id)
            _submit_accepted(db, user.id, two_sum.id)
        finally:
            db.close()

        resp = client.get("/api/coding/progress", headers=headers)
        data = resp.json()
        assert data["total_unique_solved"] == 2
        # Solving two-sum in arrays-strings should unlock linear-data-structures
        assert data["unlocked_modules_count"] == 3  # Foundations + Arrays + Linear

    def test_progress_includes_module_summaries(self):
        """Progress response includes all 6 module summaries."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
        finally:
            db.close()

        resp = client.get("/api/coding/progress", headers=headers)
        data = resp.json()
        assert len(data["modules"]) == 6

    def test_progress_percentage_calculation(self):
        """Progress percentage is correctly calculated."""
        db = TestSession()
        try:
            _seed_original_six(db)
            user, headers = _create_user(db)
            # Solve 3 of 6 problems → 50%
            for slug in ["palindrome-check", "reverse-string", "two-sum"]:
                prob = db.query(CodingProblem).filter(CodingProblem.slug == slug).first()
                _submit_accepted(db, user.id, prob.id)
        finally:
            db.close()

        resp = client.get("/api/coding/progress", headers=headers)
        data = resp.json()
        assert data["total_unique_solved"] == 3
        assert data["overall_progress_percent"] == round(3 / 48 * 100, 1)


# ═══════════════════════════════════════════════════════════════════════════
#  7. DATA INTEGRITY — SUBMISSIONS PRESERVED
# ═══════════════════════════════════════════════════════════════════════════

class TestDataIntegrity:
    def test_seeding_preserves_submissions(self):
        """Existing submissions are not deleted when re-seeding modules."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            prob = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user.id, prob.id)
            _submit_wrong(db, user.id, prob.id)

            sub_count_before = db.query(CodingSubmission).count()
            seed_coding_system_if_needed(db)  # Re-seed
            sub_count_after = db.query(CodingSubmission).count()

            assert sub_count_after == sub_count_before
        finally:
            db.close()

    def test_module_state_tracks_solved_count_correctly(self):
        """Module state solved_problems matches the user's unique solves in that module."""
        db = TestSession()
        try:
            user, _ = _create_user(db)
            _seed_original_six(db)

            palindrome = db.query(CodingProblem).filter(CodingProblem.slug == "palindrome-check").first()
            reverse_str = db.query(CodingProblem).filter(CodingProblem.slug == "reverse-string").first()
            _submit_accepted(db, user.id, palindrome.id)
            _submit_accepted(db, user.id, reverse_str.id)

            states = compute_module_unlock_states(db, user.id)
            arrays = db.query(CodingModule).filter(CodingModule.slug == "arrays-strings").first()

            assert states[arrays.id]["solved_problems"] == 2
            assert states[arrays.id]["total_problems"] == 8
        finally:
            db.close()

    def test_user_isolation(self):
        """User A's progress does not affect User B's progress."""
        db = TestSession()
        try:
            user_a, _ = _create_user(db, email="a@test.com", name="User A")
            user_b, _ = _create_user(db, email="b@test.com", name="User B")
            _seed_original_six(db)

            prob = db.query(CodingProblem).filter(CodingProblem.slug == "two-sum").first()
            _submit_accepted(db, user_a.id, prob.id)

            solved_a = get_user_unique_solved_problem_ids(db, user_a.id)
            solved_b = get_user_unique_solved_problem_ids(db, user_b.id)

            assert len(solved_a) == 1
            assert len(solved_b) == 0
        finally:
            db.close()
