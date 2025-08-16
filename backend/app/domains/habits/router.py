"""Habits router."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.core.container import ServiceContainerDep
from app.domains.habits.schemas import HabitCreate, HabitPublic, HabitsPublic, HabitUpdate
from app.domains.shared.dependencies import CurrentUser
from app.domains.shared.schemas import MessageResponse

router = APIRouter(prefix="/habits", tags=["habits"])


@router.get("/", response_model=HabitsPublic)
def read_habits(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100
) -> Any:
    """Retrieve habits."""
    return container.habit_service.get_habits(current_user, skip=skip, limit=limit)


@router.get("/{id}", response_model=HabitPublic)
def read_habit(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    id: uuid.UUID
) -> Any:
    """Get habit by ID."""
    return container.habit_service.get_habit_by_id(id, current_user)


@router.post("/", response_model=HabitPublic)
def create_habit(
    *, 
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    habit_in: HabitCreate
) -> Any:
    """Create new habit."""
    return container.habit_service.create_habit(habit_in, current_user)


@router.put("/{id}", response_model=HabitPublic)
def update_habit(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    habit_in: HabitUpdate,
) -> Any:
    """Update a habit."""
    return container.habit_service.update_habit(id, habit_in, current_user)


@router.delete("/{id}", response_model=MessageResponse)
def delete_habit(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    id: uuid.UUID
) -> MessageResponse:
    """Delete a habit."""
    return container.habit_service.delete_habit(id, current_user)