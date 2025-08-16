"""User repository."""

from typing import Optional

from sqlmodel import Session, select

from app.domains.shared.repository import BaseRepository
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with user-specific operations."""
    
    def __init__(self, session: Session):
        super().__init__(User, session)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get active users."""
        return self.get_multi(skip=skip, limit=limit, filters={"is_active": True})
    
    def get_superusers(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get superusers."""
        return self.get_multi(skip=skip, limit=limit, filters={"is_superuser": True})