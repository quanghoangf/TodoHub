"""Item domain schemas."""

import uuid

from pydantic import Field

from app.domains.shared.schemas import BaseEntitySchema, BaseSchema, PaginatedResponse


class ItemBase(BaseSchema):
    """Base item schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    """Item creation schema."""
    
    pass


class ItemUpdate(BaseSchema):
    """Item update schema."""
    
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemPublic(ItemBase, BaseEntitySchema):
    """Public item schema (for API responses)."""
    
    owner_id: uuid.UUID


class ItemsPublic(PaginatedResponse[ItemPublic]):
    """Paginated items response."""
    
    pass