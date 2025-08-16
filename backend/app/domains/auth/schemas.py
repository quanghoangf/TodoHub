"""Authentication domain schemas."""

from pydantic import EmailStr, Field

from app.domains.shared.schemas import BaseSchema, MessageResponse


class LoginRequest(BaseSchema):
    """Login request schema."""
    
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    """Token response schema."""
    
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    
    token: str
    new_password: str = Field(min_length=8, max_length=40)