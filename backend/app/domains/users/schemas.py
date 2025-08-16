"""User domain schemas."""

import uuid

from pydantic import EmailStr, Field

from app.domains.shared.schemas import BaseEntitySchema, BaseSchema, PaginatedResponse


class UserBase(BaseSchema):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    timezone: str = Field(default="UTC", max_length=50)


class UserCreate(UserBase):
    """User creation schema."""
    
    password: str = Field(..., min_length=8, max_length=40)


class UserUpdate(BaseSchema):
    """User update schema."""
    
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)
    is_active: bool | None = None
    is_superuser: bool | None = None
    timezone: str | None = Field(default=None, max_length=50)


class UserUpdateMe(BaseSchema):
    """User self-update schema."""
    
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=50)


class UserRegister(BaseSchema):
    """User registration schema."""
    
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    timezone: str = Field(default="UTC", max_length=50)


class UpdatePassword(BaseSchema):
    """Password update schema."""
    
    current_password: str = Field(..., min_length=8, max_length=40)
    new_password: str = Field(..., min_length=8, max_length=40)


class UpdateTimezone(BaseSchema):
    """Timezone update schema."""
    
    timezone: str = Field(..., max_length=50)


class UserPublic(UserBase, BaseEntitySchema):
    """Public user schema (for API responses)."""
    
    pass


class UserInDB(UserPublic):
    """User schema with sensitive fields for internal use."""
    
    hashed_password: str


class UsersPublic(PaginatedResponse[UserPublic]):
    """Paginated users response."""
    
    pass