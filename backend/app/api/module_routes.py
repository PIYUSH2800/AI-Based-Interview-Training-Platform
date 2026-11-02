"""
module_routes.py

API endpoints for the progressive coding learning system:
  - GET /api/coding/modules          → list all modules with unlock state + progress
  - GET /api/coding/modules/{slug}   → module detail with problems + solved status
  - GET /api/coding/progress         → overall user coding progress summary
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import CodingModule, CodingProblem, User
from app.schemas.schemas import CodingModuleSummary, CodingModuleDetail, CodingProblemSummary, UserCodingProgressResponse
from app.api.profile_routes import get_current_user, get_current_user_optional
from app.services.coding_progress import (
    seed_coding_system_if_needed,
    compute_module_unlock_states,
    get_user_unique_solved_problem_ids,
    check_problem_access,
)

router = APIRouter(
    prefix="/api/coding",
    tags=["Coding Modules"],
)


@router.get("/modules", response_model=List[CodingModuleSummary])
def list_modules(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Returns all coding modules with progress and unlock state for the
    authenticated user (or default unlock states for anonymous users).
    """
    seed_coding_system_if_needed(db)
    user_id = current_user.id if current_user else None
    states = compute_module_unlock_states(db, user_id)

    result = []
    for mod_id in sorted(states.keys(), key=lambda mid: states[mid]["order_index"]):
        result.append(CodingModuleSummary(**states[mod_id]))
    return result


@router.get("/modules/{module_slug}", response_model=CodingModuleDetail)
def get_module_detail(
    module_slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Returns module metadata plus its problems (with solved/locked status per user).
    """
    seed_coding_system_if_needed(db)

    module = db.query(CodingModule).filter(CodingModule.slug == module_slug).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_slug}' not found",
        )

    user_id = current_user.id if current_user else None
    states = compute_module_unlock_states(db, user_id)
    mod_state = states.get(module.id, {})

    solved_ids = get_user_unique_solved_problem_ids(db, user_id)

    problems = (
        db.query(CodingProblem)
        .filter(CodingProblem.module_id == module.id)
        .order_by(CodingProblem.order_index)
        .all()
    )

    problem_summaries = []
    for p in problems:
        is_solved = p.id in solved_ids
        is_locked = not mod_state.get("is_unlocked", True) and not is_solved
        problem_summaries.append(
            CodingProblemSummary(
                id=p.id,
                title=p.title,
                slug=p.slug,
                difficulty=p.difficulty,
                category=p.category,
                module_id=p.module_id,
                order_index=p.order_index,
                is_solved=is_solved,
                is_locked=is_locked,
            )
        )

    return CodingModuleDetail(
        id=mod_state.get("id", module.id),
        slug=mod_state.get("slug", module.slug),
        title=mod_state.get("title", module.title),
        description=mod_state.get("description", module.description),
        order_index=mod_state.get("order_index", module.order_index),
        icon_name=mod_state.get("icon_name", module.icon_name or "Code"),
        prerequisite_module_id=mod_state.get("prerequisite_module_id", module.prerequisite_module_id),
        required_prerequisite_count=mod_state.get("required_prerequisite_count", module.required_prerequisite_count),
        total_problems=mod_state.get("total_problems", len(problems)),
        solved_problems=mod_state.get("solved_problems", 0),
        is_unlocked=mod_state.get("is_unlocked", True),
        unlock_requirement=mod_state.get("unlock_requirement", "Available"),
        problems=problem_summaries,
    )


@router.get("/progress", response_model=UserCodingProgressResponse)
def get_user_coding_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the user's overall coding progress across all modules.
    Requires authentication.
    """
    seed_coding_system_if_needed(db)

    user_id = current_user.id
    states = compute_module_unlock_states(db, user_id)
    solved_ids = get_user_unique_solved_problem_ids(db, user_id)

    total_problems = db.query(CodingProblem).filter(CodingProblem.module_id.isnot(None)).count()
    total_unique_solved = len(solved_ids)
    overall_pct = round((total_unique_solved / total_problems) * 100, 1) if total_problems > 0 else 0.0

    unlocked_count = sum(1 for s in states.values() if s["is_unlocked"])

    modules_list = []
    for mod_id in sorted(states.keys(), key=lambda mid: states[mid]["order_index"]):
        modules_list.append(CodingModuleSummary(**states[mod_id]))

    return UserCodingProgressResponse(
        total_problems=total_problems,
        total_unique_solved=total_unique_solved,
        overall_progress_percent=overall_pct,
        unlocked_modules_count=unlocked_count,
        total_modules_count=len(states),
        modules=modules_list,
    )
