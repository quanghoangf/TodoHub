"""Authentication domain models."""

from sqlmodel import SQLModel


class Token(SQLModel):
    """JWT token model."""
    
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token."""
    
    sub: str | None = None