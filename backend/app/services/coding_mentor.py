"""
coding_mentor.py

Personalized recommendation engine and skill analytics service for coding practice.
Features:
- Deterministic, explainable recommendation logic
- Categories: Continue Learning, Review Previous Mistakes, Practice Weak Topics, Increase Difficulty
- Never recommends locked problems as immediately actionable
- Skill analytics grounded in real database records
- Graceful handling of new users with 0 submissions
"""

from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.models import CodingProblem, CodingSubmission, CodingModule
from app.services.coding_progress import (
    compute_module_unlock_states,
    get_user_unique_solved_problem_ids,
)


def get_problem_recommendations(db: Session, user_id: int) -> dict:
    """
    Generates personalized, explainable problem recommendations for a user.
    Never recommends locked problems.
    """
    all_problems = db.query(CodingProblem).order_by(CodingProblem.module_id, CodingProblem.order_index).all()
    unique_solved_ids = get_user_unique_solved_problem_ids(db, user_id)
    unlock_states = compute_module_unlock_states(db, user_id)

    # Filter accessible problems (unlocked module or already solved)
    accessible_problems = [
        p for p in all_problems
        if (p.module_id and unlock_states.get(p.module_id, {}).get("is_unlocked", False))
        or p.id in unique_solved_ids
    ]
    accessible_ids = {p.id for p in accessible_problems}

    # Fetch user submissions
    submissions = (
        db.query(CodingSubmission)
        .filter(CodingSubmission.user_id == user_id)
        .order_by(desc(CodingSubmission.created_at))
        .all()
    )

    recommendations = []
    selected_problem_ids: Set[int] = set()

    # Track submission metrics per problem and per category
    problem_attempts: Dict[int, int] = {}
    problem_failed_attempts: Dict[int, int] = {}
    problem_latest_status: Dict[int, str] = {}
    category_attempts: Dict[str, int] = {}
    category_fails: Dict[str, int] = {}
    category_solves: Dict[str, int] = {}

    for sub in submissions:
        pid = sub.problem_id
        problem_attempts[pid] = problem_attempts.get(pid, 0) + 1
        if pid not in problem_latest_status:
            problem_latest_status[pid] = sub.status

        prob = next((p for p in all_problems if p.id == pid), None)
        cat = prob.category if prob else "General"

        category_attempts[cat] = category_attempts.get(cat, 0) + 1
        if sub.status != "accepted":
            problem_failed_attempts[pid] = problem_failed_attempts.get(pid, 0) + 1
            category_fails[cat] = category_fails.get(cat, 0) + 1
        else:
            category_solves[cat] = category_solves.get(cat, 0) + 1

    # Identify currently active unlocked module (lowest unlocked module with unsolved problems)
    unlocked_modules = [m for m_id, m in unlock_states.items() if m.get("is_unlocked")]
    unlocked_modules.sort(key=lambda x: x.get("order_index", 1))

    active_module_id = None
    active_module_title = "Foundations"
    for m in unlocked_modules:
        if m.get("solved_problems", 0) < m.get("total_problems", 0):
            active_module_id = m.get("id")
            active_module_title = m.get("title", "")
            break
    if not active_module_id and unlocked_modules:
        active_module_id = unlocked_modules[-1].get("id")
        active_module_title = unlocked_modules[-1].get("title", "")

    # Helper to add recommendation
    def add_rec(prob: CodingProblem, category_type: str, reason_text: str, priority_val: int):
        if prob.id not in selected_problem_ids and prob.id in accessible_ids:
            selected_problem_ids.add(prob.id)
            recommendations.append({
                "problem": {
                    "id": prob.id,
                    "title": prob.title,
                    "slug": prob.slug,
                    "difficulty": prob.difficulty,
                    "category": prob.category,
                    "module_id": prob.module_id,
                    "order_index": prob.order_index,
                    "is_solved": prob.id in unique_solved_ids,
                    "is_locked": False,
                },
                "category": category_type,
                "reason": reason_text,
                "priority": priority_val,
            })

    # --- Category 1: Continue Learning ---
    # Pick next unsolved problem in current active module
    candidate_c1 = [
        p for p in accessible_problems
        if p.module_id == active_module_id and p.id not in unique_solved_ids
    ]
    if candidate_c1:
        c1_prob = candidate_c1[0]
        add_rec(
            c1_prob,
            "Continue Learning",
            f"Recommended because this is your next milestone in '{active_module_title}', reinforcing {c1_prob.category} concepts.",
            1
        )
    elif accessible_problems:
        # If active module is completed, pick any unsolved accessible problem
        unsolved_accessible = [p for p in accessible_problems if p.id not in unique_solved_ids]
        if unsolved_accessible:
            c1_prob = unsolved_accessible[0]
            add_rec(
                c1_prob,
                "Continue Learning",
                f"Recommended to expand your breadth in {c1_prob.category}.",
                1
            )

    # --- Category 2: Review Previous Mistakes ---
    # Pick problem attempted by user with a failure, but not yet solved
    mistake_candidates = [
        p for p in accessible_problems
        if p.id in problem_failed_attempts and p.id not in unique_solved_ids
    ]
    if mistake_candidates:
        # Sort by most recent attempts or failure count
        mistake_candidates.sort(key=lambda p: problem_failed_attempts.get(p.id, 0), reverse=True)
        m_prob = mistake_candidates[0]
        fails = problem_failed_attempts.get(m_prob.id, 1)
        add_rec(
            m_prob,
            "Review Previous Mistakes",
            f"Recommended because you attempted this challenge ({fails} attempt{'s' if fails > 1 else ''} with errors). Review edge cases and retry.",
            2
        )

    # --- Category 3: Practice Weak Topics ---
    # Find topic with highest failure rate and >= 1 attempt
    weakest_cat = None
    highest_fail_rate = -1.0
    for cat, attempts in category_attempts.items():
        fails = category_fails.get(cat, 0)
        rate = fails / attempts if attempts > 0 else 0
        if rate > highest_fail_rate and rate > 0:
            highest_fail_rate = rate
            weakest_cat = cat

    if weakest_cat:
        cat_candidates = [
            p for p in accessible_problems
            if p.category == weakest_cat and p.id not in unique_solved_ids and p.id not in selected_problem_ids
        ]
        if cat_candidates:
            w_prob = cat_candidates[0]
            pct = int(highest_fail_rate * 100)
            add_rec(
                w_prob,
                "Practice Weak Topics",
                f"Recommended because you have a {pct}% error rate on {weakest_cat} problems. This challenge reinforces foundational patterns.",
                3
            )

    # Fallback for weak topic if no attempts yet or all attempted solved:
    if "Practice Weak Topics" not in [r["category"] for r in recommendations]:
        # Recommend foundational topic challenge
        foundational_candidates = [
            p for p in accessible_problems
            if p.id not in unique_solved_ids and p.id not in selected_problem_ids
        ]
        if foundational_candidates:
            f_prob = foundational_candidates[0]
            add_rec(
                f_prob,
                "Practice Weak Topics",
                f"Recommended to build core confidence in {f_prob.category} and prevent common algorithmic pitfalls.",
                3
            )

    # --- Category 4: Increase Difficulty ---
    # If user has solved Easy problems in an accessible category/module, recommend Medium/Hard
    solved_problems_objs = [p for p in all_problems if p.id in unique_solved_ids]
    has_easy_solves = any(p.difficulty == "Easy" for p in solved_problems_objs)

    if has_easy_solves:
        medium_hard_candidates = [
            p for p in accessible_problems
            if p.difficulty in ["Medium", "Hard"] and p.id not in unique_solved_ids and p.id not in selected_problem_ids
        ]
        if medium_hard_candidates:
            mh_prob = medium_hard_candidates[0]
            add_rec(
                mh_prob,
                "Increase Difficulty",
                f"Recommended because you have demonstrated proficiency on Easy problems. Level up to this {mh_prob.difficulty} challenge to practice advanced optimization.",
                4
            )

    # New user onboarding fallback: Ensure at least 3 high-quality actionable recommendations
    if len(recommendations) < 3:
        for p in accessible_problems:
            if p.id not in selected_problem_ids and p.id not in unique_solved_ids:
                add_rec(
                    p,
                    "Continue Learning",
                    f"Recommended starting problem in {p.category} to build interview readiness.",
                    len(recommendations) + 1
                )
            if len(recommendations) >= 4:
                break

    return {
        "total_recommended": len(recommendations),
        "recommendations": recommendations,
    }


def get_user_skill_analytics(db: Session, user_id: int) -> dict:
    """
    Computes personalized skill statistics grounded strictly in real database records.
    Handles new users gracefully without NaN or division by zero.
    """
    all_problems = db.query(CodingProblem).all()
    total_problems_count = len(all_problems)
    unique_solved_ids = get_user_unique_solved_problem_ids(db, user_id)

    submissions = (
        db.query(CodingSubmission)
        .filter(CodingSubmission.user_id == user_id)
        .all()
    )

    total_submissions = len(submissions)
    accepted_submissions = sum(1 for s in submissions if s.status == "accepted")
    overall_acceptance_rate = (
        round((accepted_submissions / total_submissions) * 100, 1)
        if total_submissions > 0
        else 0.0
    )

    # 1. Difficulty Breakdown
    diff_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    diff_solves = {"Easy": 0, "Medium": 0, "Hard": 0}
    diff_attempts = {"Easy": 0, "Medium": 0, "Hard": 0}
    diff_accepted = {"Easy": 0, "Medium": 0, "Hard": 0}

    for p in all_problems:
        d = p.difficulty if p.difficulty in diff_counts else "Easy"
        diff_counts[d] += 1
        if p.id in unique_solved_ids:
            diff_solves[d] += 1

    for s in submissions:
        prob = next((p for p in all_problems if p.id == s.problem_id), None)
        if prob:
            d = prob.difficulty if prob.difficulty in diff_attempts else "Easy"
            diff_attempts[d] += 1
            if s.status == "accepted":
                diff_accepted[d] += 1

    difficulty_breakdown = []
    for diff in ["Easy", "Medium", "Hard"]:
        attempts = diff_attempts[diff]
        succ_rate = round((diff_accepted[diff] / attempts) * 100, 1) if attempts > 0 else 0.0
        difficulty_breakdown.append({
            "difficulty": diff,
            "total_problems": diff_counts[diff],
            "solved_problems": diff_solves[diff],
            "attempts": attempts,
            "success_rate": succ_rate,
        })

    # 2. Topic Breakdown
    topic_problems: Dict[str, int] = {}
    topic_solves: Dict[str, int] = {}
    topic_attempts: Dict[str, int] = {}
    topic_accepted: Dict[str, int] = {}

    for p in all_problems:
        cat = p.category or "General"
        topic_problems[cat] = topic_problems.get(cat, 0) + 1
        if p.id in unique_solved_ids:
            topic_solves[cat] = topic_solves.get(cat, 0) + 1

    for s in submissions:
        prob = next((p for p in all_problems if p.id == s.problem_id), None)
        if prob:
            cat = prob.category or "General"
            topic_attempts[cat] = topic_attempts.get(cat, 0) + 1
            if s.status == "accepted":
                topic_accepted[cat] = topic_accepted.get(cat, 0) + 1

    topic_breakdown = []
    stronger_topics = []
    topics_needing_practice = []

    for cat in sorted(topic_problems.keys()):
        attempts = topic_attempts.get(cat, 0)
        solves = topic_solves.get(cat, 0)
        acc = topic_accepted.get(cat, 0)
        rate = round((acc / attempts) * 100, 1) if attempts > 0 else 0.0

        topic_breakdown.append({
            "topic": cat,
            "total_problems": topic_problems[cat],
            "solved_problems": solves,
            "attempts": attempts,
            "success_rate": rate,
        })

        if solves >= 1 and (rate >= 60.0 or attempts == solves):
            stronger_topics.append(cat)
        elif attempts > 0 and rate < 60.0:
            topics_needing_practice.append(cat)

    # 3. Suggested Next Steps
    suggested_next_steps = []
    if total_submissions == 0:
        suggested_next_steps.append("Start with Module 1: Foundations & Logic to calibrate your coding rhythm.")
        suggested_next_steps.append("Practice writing in Python, Java, or C++ and running against sample test cases.")
    else:
        if topics_needing_practice:
            first_weak = topics_needing_practice[0]
            suggested_next_steps.append(f"Revisit failed submissions in {first_weak}; walk through step-by-step logic before running code.")
        if diff_solves["Easy"] >= 4 and diff_solves["Medium"] < 2:
            suggested_next_steps.append("You have established strong momentum on Easy problems; tackle Medium challenges to practice logarithmic and dynamic programming approaches.")
        if len(unique_solved_ids) < total_problems_count:
            next_unsolved = next((p for p in all_problems if p.id not in unique_solved_ids), None)
            if next_unsolved:
                suggested_next_steps.append(f"Advance your curriculum progress by solving '{next_unsolved.title}'.")

    return {
        "total_unique_solved": len(unique_solved_ids),
        "total_problems": total_problems_count,
        "total_submissions": total_submissions,
        "overall_acceptance_rate": overall_acceptance_rate,
        "difficulty_breakdown": difficulty_breakdown,
        "topic_breakdown": topic_breakdown,
        "stronger_topics": stronger_topics[:4],
        "topics_needing_practice": topics_needing_practice[:4],
        "suggested_next_steps": suggested_next_steps,
    }
