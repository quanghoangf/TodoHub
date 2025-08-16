"""Item domain models."""

import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.domains.shared.models import BaseModel

if TYPE_CHECKING:
    from app.domains.users.models import User


class Item(BaseModel, table=True):
    """Item database model."""
    
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", 
        nullable=False, 
        ondelete="CASCADE"
    )
    
    # Relationships
    owner: "User" = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"lazy": "select"}
    )