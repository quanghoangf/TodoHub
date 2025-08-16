"""User domain models."""

from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.domains.shared.models import BaseModel

if TYPE_CHECKING:
    from app.domains.items.models import Item


class User(BaseModel, table=True):
    """User database model."""
    
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    
    # Relationships
    items: list["Item"] = Relationship(
        back_populates="owner", 
        cascade_delete=True,
        sa_relationship_kwargs={"lazy": "select"}
    )