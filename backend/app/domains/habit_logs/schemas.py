"""Habit logs domain schemas."""

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import Field

from app.domains.shared.schemas import BaseSchema


class HabitLogBase(BaseSchema):
    """Base habit log schema."""
    local_date: date = Field(..., description="Date in user's timezone")
    meta: Optional[dict] = Field(default=None, description="Additional metadata")


class HabitLogCreate(HabitLogBase):
    """Schema for creating a habit log."""
    idempotency_key: Optional[str] = Field(default=None, max_length=255)


class HabitLogPublic(HabitLogBase):
    """Public habit log schema."""
    id: uuid.UUID
    habit_id: uuid.UUID
    user_id: uuid.UUID
    recorded_at: datetime
    idempotency_key: Optional[str] = None


class HabitLogsPublic(BaseSchema):
    """Public schema for multiple habit logs."""
    data: list[HabitLogPublic]
    count: int


class StreakResponse(BaseSchema):
    """Schema for streak information."""
    habit_id: uuid.UUID
    current_streak: int = Field(..., description="Current consecutive days")
    longest_streak: int = Field(..., description="Longest streak ever")
    last_updated: datetime


class HabitLogDelete(BaseSchema):
    """Schema for deleting a habit log."""
    local_date: date = Field(..., description="Date to delete log for")