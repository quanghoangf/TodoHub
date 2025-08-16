"""Habit domain models."""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, JSON

from app.domains.shared.models import BaseModel

if TYPE_CHECKING:
    from app.domains.users.models import User


class Habit(BaseModel, table=True):
    """Habit database model."""
    
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    schedule: dict = Field(default={"type": "daily"}, sa_type=JSON)
    start_date: date | None = Field(default=None)
    backfill_window_hours: int = Field(default=48)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", 
        nullable=False, 
        ondelete="CASCADE"
    )
    
    # Relationships
    owner: "User" = Relationship(
        back_populates="habits",
        sa_relationship_kwargs={"lazy": "select"}
    )