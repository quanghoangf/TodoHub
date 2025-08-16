"""Habit logs API router."""

import uuid
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.domains.shared.dependencies import CurrentUser
from app.core.container import ServiceContainerDep
from app.domains.habit_logs.schemas import (
    HabitLogCreate,
    HabitLogPublic,
    HabitLogsPublic,
    StreakResponse,
)
from app.domains.shared.schemas import MessageResponse

router = APIRouter(prefix="/habits")


@router.post("/{habit_id}/logs", response_model=HabitLogPublic)
def log_habit_completion(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
    log_data: HabitLogCreate,
) -> Any:
    """
    Log a habit completion.
    
    This endpoint is idempotent - logging the same habit on the same date
    multiple times will return the existing log without creating duplicates.
    """
    return container.habit_log_service.log_habit(habit_id, log_data, current_user)


@router.get("/{habit_id}/logs", response_model=HabitLogsPublic)
def get_habit_logs(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
    skip: int = Query(default=0, ge=0, description="Number of logs to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of logs to return"),
) -> Any:
    """Get habit completion logs."""
    return container.habit_log_service.get_habit_logs(
        habit_id, current_user, skip, limit
    )


@router.get("/{habit_id}/streak", response_model=StreakResponse)
def get_habit_streak(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
) -> Any:
    """Get habit streak information including current and longest streaks."""
    return container.habit_log_service.get_habit_streak(habit_id, current_user)


@router.delete("/{habit_id}/logs/{log_date}", response_model=MessageResponse)
def delete_habit_log(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
    log_date: date,
) -> Any:
    """
    Delete a habit log for a specific date.
    
    This will recalculate the streak after deletion.
    """
    return container.habit_log_service.delete_habit_log(
        habit_id, log_date, current_user
    )