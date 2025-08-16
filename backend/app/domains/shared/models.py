"""Shared database models and base classes."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


class BaseModel(TimestampMixin):
    """Base model with common fields."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)