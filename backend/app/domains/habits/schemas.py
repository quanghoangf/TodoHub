"""Habit domain schemas."""

import uuid
from datetime import date
from typing import Dict, Any

from pydantic import Field, validator

from app.domains.shared.schemas import BaseEntitySchema, BaseSchema, PaginatedResponse


class HabitBase(BaseSchema):
    """Base habit schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    schedule: Dict[str, Any] = Field(default={"type": "daily"})
    start_date: date | None = Field(default=None)
    backfill_window_hours: int = Field(default=48, ge=0, le=168)  # Max 1 week
    
    @field_validator('schedule')
    @classmethod
    def validate_schedule(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate schedule format."""
        if not isinstance(v, dict):
            raise ValueError('Schedule must be a dictionary')

        schedule_type = v.get('type')
        if schedule_type not in ['daily', 'weekly', 'custom']:
            raise ValueError('Schedule type must be daily, weekly, or custom')

        if schedule_type == 'weekly':
            days = v.get('days', [])
            if not isinstance(days, list) or not all(isinstance(d, int) and 0 <= d <= 6 for d in days):
                raise ValueError('Weekly schedule must include valid days (0-6)')

        if schedule_type == 'custom':
            interval = v.get('interval', 1)
            if not isinstance(interval, int) or interval < 1:
                raise ValueError('Custom schedule interval must be a positive integer')

        return v

class HabitCreate(HabitBase):
    """Habit creation schema."""
    
    pass


class HabitUpdate(BaseSchema):
    """Habit update schema."""
    
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    schedule: Dict[str, Any] | None = Field(default=None)
    start_date: date | None = Field(default=None)
    backfill_window_hours: int | None = Field(default=None, ge=0, le=168)
    
    @validator('schedule')
    def validate_schedule(cls, v):
        """Validate schedule format if provided."""
        if v is None:
            return v
        return HabitBase.validate_schedule(v)


class HabitPublic(HabitBase, BaseEntitySchema):
    """Public habit schema (for API responses)."""
    
    owner_id: uuid.UUID


class HabitsPublic(PaginatedResponse[HabitPublic]):
    """Paginated habits response."""
    
    pass