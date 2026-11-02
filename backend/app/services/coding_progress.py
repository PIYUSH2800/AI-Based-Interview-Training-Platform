"""
coding_progress.py

Service for managing coding modules, user progress computation, and module unlock rules.
Rules:
  - Progress tracks unique accepted problems per user (duplicates do not inflate count).
  - Failed or partially correct submissions do not count.
  - Reattempts of already-solved problems are always permitted.
  - Module unlock checks evaluate prerequisites server-side and are isolated per user.
"""

from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.models.models import CodingModule, CodingProblem, TestCase, CodingSubmission

# ── 1. Module Definitions (Explicit ordering & prerequisite milestones) ─────────

MODULE_DEFINITIONS = [
    {
        "order_index": 1,
        "slug": "foundations-logic",
        "title": "Foundations & Logic",
        "description": "Essential programming fundamentals, control flow, arithmetic, and basic logic.",
        "icon_name": "Cpu",
        "prerequisite_slug": None,
        "required_prerequisite_count": 0,
    },
    {
        "order_index": 2,
        "slug": "arrays-strings",
        "title": "Arrays & Strings",
        "description": "Array traversal, two-pointer techniques, string manipulation, and hashing.",
        "icon_name": "Layers",
        "prerequisite_slug": None,  # Foundational data structure module, unlocked by default
        "required_prerequisite_count": 0,
    },
    {
        "order_index": 3,
        "slug": "linear-data-structures",
        "title": "Linear Data Structures",
        "description": "Stacks, queues, linked lists, and monotonic structures.",
        "icon_name": "GitCommit",
        "prerequisite_slug": "arrays-strings",
        "required_prerequisite_count": 1,  # Must solve at least 1 problem in Arrays & Strings
    },
    {
        "order_index": 4,
        "slug": "searching-sorting-recursion",
        "title": "Searching, Sorting & Recursion",
        "description": "Binary search, divide-and-conquer, recursive problem decomposition, and sorting patterns.",
        "icon_name": "Search",
        "prerequisite_slug": "linear-data-structures",
        "required_prerequisite_count": 1,  # Must solve at least 1 problem in Linear Data Structures
    },
    {
        "order_index": 5,
        "slug": "trees-heaps-graphs",
        "title": "Trees, Heaps & Graphs",
        "description": "Binary tree traversals, BST validation, priority queues, and graph search (BFS/DFS).",
        "icon_name": "GitBranch",
        "prerequisite_slug": "searching-sorting-recursion",
        "required_prerequisite_count": 1,  # Must solve at least 1 problem in Searching, Sorting & Recursion
    },
    {
        "order_index": 6,
        "slug": "dynamic-programming-advanced",
        "title": "Dynamic Programming & Advanced",
        "description": "Optimal substructure, memoization, bottom-up DP, and complex greedy strategies.",
        "icon_name": "Zap",
        "prerequisite_slug": "searching-sorting-recursion",
        "required_prerequisite_count": 1,  # Must solve at least 1 problem in Searching, Sorting & Recursion
    },
]

# ── 2. Mapping of the Original Six Problems ────────────────────────────────────

from app.curriculum import (
    EXISTING_PROBLEMS_ASSIGNMENTS,
    ALL_NEW_PROBLEMS,
    ALL_NEW_TEST_CASES,
)

EXISTING_PROBLEMS_MODULE_MAP = EXISTING_PROBLEMS_ASSIGNMENTS


# ── 3. Idempotent Seeding Function ───────────────────────────────────────────

def seed_coding_system_if_needed(db: Session, initial_problems_data=None, initial_test_cases_data=None):
    """
    Idempotently seeds coding modules and synchronizes problem module assignments.
    - Never deletes or resets existing tables or submissions.
    - Preserves existing problem IDs, slugs, and test-case IDs.
    - Updates module_id and order_index for the 6 existing problems.
    - Slug-based upsert for the 42 new curriculum problems.
    - Ensures exactly 48 unique problems (8 per module).
    """
    # 1. Seed or synchronize CodingModule rows
    modules_by_slug: Dict[str, CodingModule] = {}
    for m_def in MODULE_DEFINITIONS:
        mod = db.query(CodingModule).filter(CodingModule.slug == m_def["slug"]).first()
        if not mod:
            mod = CodingModule(
                slug=m_def["slug"],
                title=m_def["title"],
                description=m_def["description"],
                order_index=m_def["order_index"],
                icon_name=m_def["icon_name"],
                required_prerequisite_count=m_def["required_prerequisite_count"],
            )
            db.add(mod)
            db.flush()
        else:
            mod.title = m_def["title"]
            mod.description = m_def["description"]
            mod.order_index = m_def["order_index"]
            mod.icon_name = m_def["icon_name"]
            mod.required_prerequisite_count = m_def["required_prerequisite_count"]
        modules_by_slug[mod.slug] = mod

    # 2. Link prerequisite_module_id by slug lookup
    for m_def in MODULE_DEFINITIONS:
        prereq_slug = m_def["prerequisite_slug"]
        if prereq_slug and prereq_slug in modules_by_slug:
            target_mod = modules_by_slug.get(m_def["slug"])
            if target_mod:
                target_mod.prerequisite_module_id = modules_by_slug[prereq_slug].id

    # 3. Map the original six problems to their respective modules and orders
    for slug, mapping in EXISTING_PROBLEMS_MODULE_MAP.items():
        prob = db.query(CodingProblem).filter(CodingProblem.slug == slug).first()
        mod = modules_by_slug.get(mapping["module_slug"])
        if prob and mod:
            prob.module_id = mod.id
            prob.order_index = mapping["order_index"]

    # 4. Seed new curriculum problems (slug-based upsert)
    new_problems_to_seed = initial_problems_data if initial_problems_data is not None else ALL_NEW_PROBLEMS
    for p_data in new_problems_to_seed:
        existing = db.query(CodingProblem).filter(CodingProblem.slug == p_data["slug"]).first()
        mod_slug = p_data.get("module_slug")
        mod = modules_by_slug.get(mod_slug) if mod_slug else None
        mod_id = mod.id if mod else p_data.get("module_id")

        if not existing:
            prob = CodingProblem(
                title=p_data["title"],
                slug=p_data["slug"],
                difficulty=p_data["difficulty"],
                category=p_data["category"],
                description=p_data["description"],
                examples=p_data["examples"],
                constraints=p_data["constraints"],
                starter_code=p_data["starter_code"],
                supported_languages=p_data["supported_languages"],
                module_id=mod_id,
                order_index=p_data.get("order_index", 1),
            )
            db.add(prob)
            db.flush()
        else:
            if mod_id and existing.module_id != mod_id:
                existing.module_id = mod_id
            if "order_index" in p_data and existing.order_index != p_data["order_index"]:
                existing.order_index = p_data["order_index"]

    # 5. Seed test cases if missing
    test_cases_dict = initial_test_cases_data if initial_test_cases_data is not None else ALL_NEW_TEST_CASES
    if test_cases_dict:
        problems = db.query(CodingProblem).all()
        for prob in problems:
            tc_count = db.query(TestCase).filter(TestCase.problem_id == prob.id).count()
            if tc_count == 0 and prob.slug in test_cases_dict:
                for tc_data in test_cases_dict[prob.slug]:
                    test_case = TestCase(
                        problem_id=prob.id,
                        input=tc_data["input"],
                        expected_output=tc_data["expected_output"],
                        is_sample=tc_data["is_sample"],
                    )
                    db.add(test_case)

    db.commit()


# ── 4. User Progress & Unlock Calculation ────────────────────────────────────

def get_user_unique_solved_problem_ids(db: Session, user_id: Optional[int]) -> Set[int]:
    """
    Returns set of problem IDs that the user has successfully solved (accepted status).
    Duplicates are ignored; failed/partial submissions do not count.
    """
    if not user_id:
        return set()

    rows = (
        db.query(CodingSubmission.problem_id)
        .filter(
            CodingSubmission.user_id == user_id,
            CodingSubmission.status == "accepted",
        )
        .distinct()
        .all()
    )
    return {r[0] for r in rows}


def get_user_solved_problems_by_module(db: Session, user_id: Optional[int]) -> Dict[int, Set[int]]:
    """
    Returns a dict mapping module_id -> set of unique solved problem IDs for the user.
    """
    if not user_id:
        return {}

    rows = (
        db.query(CodingProblem.module_id, CodingSubmission.problem_id)
        .join(CodingSubmission, CodingSubmission.problem_id == CodingProblem.id)
        .filter(
            CodingSubmission.user_id == user_id,
            CodingSubmission.status == "accepted",
            CodingProblem.module_id.isnot(None),
        )
        .distinct()
        .all()
    )

    result: Dict[int, Set[int]] = {}
    for mod_id, prob_id in rows:
        result.setdefault(mod_id, set()).add(prob_id)
    return result


def compute_module_unlock_states(db: Session, user_id: Optional[int]) -> Dict[int, dict]:
    """
    Evaluates unlock status, solved count, and unlock requirement for all modules.
    Isolated per user; computed entirely server-side.
    """
    modules = db.query(CodingModule).order_by(CodingModule.order_index).all()
    solved_by_mod = get_user_solved_problems_by_module(db, user_id)

    mod_dict: Dict[int, CodingModule] = {m.id: m for m in modules}
    states: Dict[int, dict] = {}

    for mod in modules:
        total_in_mod = db.query(CodingProblem).filter(CodingProblem.module_id == mod.id).count()
        solved_in_mod = len(solved_by_mod.get(mod.id, set()))

        is_unlocked = False
        unlock_requirement = "Available"

        # Module with no prerequisite is unlocked by default
        if mod.prerequisite_module_id is None or mod.required_prerequisite_count == 0:
            is_unlocked = True
        else:
            prereq = mod_dict.get(mod.prerequisite_module_id)
            prereq_title = prereq.title if prereq else "prerequisite module"
            prereq_solved_count = len(solved_by_mod.get(mod.prerequisite_module_id, set())) if user_id else 0

            if prereq_solved_count >= mod.required_prerequisite_count:
                is_unlocked = True
            else:
                remaining = mod.required_prerequisite_count - prereq_solved_count
                unlock_requirement = f"Solve {remaining} more problem(s) in '{prereq_title}' to unlock"

        states[mod.id] = {
            "id": mod.id,
            "slug": mod.slug,
            "title": mod.title,
            "description": mod.description,
            "order_index": mod.order_index,
            "icon_name": mod.icon_name,
            "prerequisite_module_id": mod.prerequisite_module_id,
            "required_prerequisite_count": mod.required_prerequisite_count,
            "total_problems": total_in_mod,
            "solved_problems": solved_in_mod,
            "is_unlocked": is_unlocked,
            "unlock_requirement": unlock_requirement,
        }

    return states


def check_problem_access(db: Session, problem: CodingProblem, user_id: Optional[int]) -> Tuple[bool, Optional[str]]:
    """
    Checks whether a user can access, run, or submit a given coding problem.
    Rules:
      1. A user who has already solved the problem can ALWAYS access and reattempt it.
      2. If problem has no module assigned, it is accessible.
      3. If problem's module is unlocked for the user, it is accessible.
      4. If problem's module is locked, returns (False, reason).
    """
    if not problem:
        return False, "Problem not found."

    # If user already solved it, always allow reattempts
    if user_id:
        user_solved_ids = get_user_unique_solved_problem_ids(db, user_id)
        if problem.id in user_solved_ids:
            return True, None

    # If problem has no module, it is accessible
    if not problem.module_id:
        return True, None

    # Check module unlock status
    module_states = compute_module_unlock_states(db, user_id)
    mod_state = module_states.get(problem.module_id)

    if not mod_state or mod_state["is_unlocked"]:
        return True, None

    return False, f"Problem is locked. {mod_state['unlock_requirement']}."
