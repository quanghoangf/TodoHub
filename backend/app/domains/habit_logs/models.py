"""Habit logs domain models."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, JSON, UniqueConstraint, SQLModel

from app.domains.shared.models import BaseModel

if TYPE_CHECKING:
    from app.domains.habits.models import Habit
    from app.domains.users.models import User


class HabitLog(BaseModel, table=True):
    """Habit log database model for tracking habit completions."""
    
    __tablename__ = "habit_logs"
    
    habit_id: uuid.UUID = Field(
        foreign_key="habit.id", 
        nullable=False, 
        ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", 
        nullable=False, 
        ondelete="CASCADE"
    )
    local_date: date = Field(nullable=False, index=True)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    idempotency_key: str | None = Field(default=None, max_length=255)
    meta: dict | None = Field(default=None, sa_type=JSON)
    
    # Relationships
    habit: "Habit" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    user: "User" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    
    class Config:
        table = True
        
    __table_args__ = (
        UniqueConstraint('habit_id', 'local_date', name='uq_habit_logs_habit_id_local_date'),
    )


class StreakCache(SQLModel, table=True):
    """Streak cache for performance optimization."""
    
    __tablename__ = "streaks_cache"
    
    habit_id: uuid.UUID = Field(
        foreign_key="habit.id", 
        nullable=False, 
        ondelete="CASCADE",
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime | None = Field(default=None, nullable=True)
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    habit: "Habit" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    
    class Config:
        table = True