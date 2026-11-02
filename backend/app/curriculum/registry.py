"""
Curriculum Registry for Checkpoint 10D.
Aggregates all 6 modules (8 problems each, 48 total) and their test cases.
Preserves the 6 original problems and adds exactly 42 new problems.
"""

from typing import Dict, List, Any
from app.curriculum.module1 import MODULE1_PROBLEMS, MODULE1_TEST_CASES
from app.curriculum.module2 import MODULE2_NEW_PROBLEMS, MODULE2_NEW_TEST_CASES
from app.curriculum.module3 import MODULE3_NEW_PROBLEMS, MODULE3_NEW_TEST_CASES
from app.curriculum.module4 import MODULE4_NEW_PROBLEMS, MODULE4_NEW_TEST_CASES
from app.curriculum.module5 import MODULE5_PROBLEMS, MODULE5_TEST_CASES
from app.curriculum.module6 import MODULE6_PROBLEMS, MODULE6_TEST_CASES

# ── Module Slugs in Canonical Order ───────────────────────────────────────────
MODULE_SLUGS = [
    "foundations-logic",
    "arrays-strings",
    "linear-data-structures",
    "searching-sorting-recursion",
    "trees-heaps-graphs",
    "dynamic-programming-advanced",
]

# ── Module Mapping for the 6 Original Problems ────────────────────────────────
EXISTING_PROBLEMS_ASSIGNMENTS = {
    "two-sum": {"module_slug": "arrays-strings", "order_index": 1},
    "reverse-string": {"module_slug": "arrays-strings", "order_index": 2},
    "palindrome-check": {"module_slug": "arrays-strings", "order_index": 3},
    "valid-parentheses": {"module_slug": "linear-data-structures", "order_index": 1},
    "binary-search": {"module_slug": "searching-sorting-recursion", "order_index": 1},
    "maximum-subarray": {"module_slug": "searching-sorting-recursion", "order_index": 2},
}

# ── New Problem Bundles ────────────────────────────────────────────────────────
NEW_PROBLEMS_BY_MODULE: Dict[str, List[Dict[str, Any]]] = {
    "foundations-logic": MODULE1_PROBLEMS,                    # 8 problems
    "arrays-strings": MODULE2_NEW_PROBLEMS,                   # 5 problems (+ 3 existing = 8)
    "linear-data-structures": MODULE3_NEW_PROBLEMS,           # 7 problems (+ 1 existing = 8)
    "searching-sorting-recursion": MODULE4_NEW_PROBLEMS,       # 6 problems (+ 2 existing = 8)
    "trees-heaps-graphs": MODULE5_PROBLEMS,                   # 8 problems
    "dynamic-programming-advanced": MODULE6_PROBLEMS,         # 8 problems
}

# All 42 new problems combined
ALL_NEW_PROBLEMS: List[Dict[str, Any]] = []
for mod_slug, probs in NEW_PROBLEMS_BY_MODULE.items():
    for p in probs:
        p_copy = dict(p)
        p_copy["module_slug"] = mod_slug
        ALL_NEW_PROBLEMS.append(p_copy)

# All new test cases combined (42 problems * 4+ test cases)
ALL_NEW_TEST_CASES: Dict[str, List[Dict[str, Any]]] = {}
ALL_NEW_TEST_CASES.update(MODULE1_TEST_CASES)
ALL_NEW_TEST_CASES.update(MODULE2_NEW_TEST_CASES)
ALL_NEW_TEST_CASES.update(MODULE3_NEW_TEST_CASES)
ALL_NEW_TEST_CASES.update(MODULE4_NEW_TEST_CASES)
ALL_NEW_TEST_CASES.update(MODULE5_TEST_CASES)
ALL_NEW_TEST_CASES.update(MODULE6_TEST_CASES)


def get_curriculum_summary() -> Dict[str, Any]:
    """Returns counts and metadata about the 48-problem curriculum."""
    total_existing = len(EXISTING_PROBLEMS_ASSIGNMENTS)
    total_new = len(ALL_NEW_PROBLEMS)
    total_problems = total_existing + total_new

    counts_by_module = {slug: 0 for slug in MODULE_SLUGS}
    for m in EXISTING_PROBLEMS_ASSIGNMENTS.values():
        counts_by_module[m["module_slug"]] += 1
    for p in ALL_NEW_PROBLEMS:
        counts_by_module[p["module_slug"]] += 1

    return {
        "total_problems": total_problems,
        "existing_problems": total_existing,
        "new_problems": total_new,
        "counts_by_module": counts_by_module,
        "total_test_case_suites": len(ALL_NEW_TEST_CASES),
    }
