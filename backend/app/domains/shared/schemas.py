"""Shared schemas and base classes."""

import uuid
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime
    updated_at: Optional[datetime] = None


class BaseEntitySchema(TimestampSchema):
    """Base entity schema with ID and timestamps."""
    
    id: uuid.UUID


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    data: List[T]
    count: int
    total: Optional[int] = None
    page: Optional[int] = None
    size: Optional[int] = None


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str