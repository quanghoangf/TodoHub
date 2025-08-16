"""Dependency injection container."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session
from app.domains.auth.service import AuthService
from app.domains.items.service import ItemService
from app.domains.users.service import UserService
from app.infrastructure.email.service import EmailService


class ServiceContainer:
    """Service container for dependency injection."""
    
    def __init__(self, session: Session):
        self.session = session
        self._auth_service = None
        self._user_service = None
        self._item_service = None
        self._email_service = None
    
    @property
    def auth_service(self) -> AuthService:
        """Get auth service instance."""
        if self._auth_service is None:
            self._auth_service = AuthService(self.session)
        return self._auth_service
    
    @property
    def user_service(self) -> UserService:
        """Get user service instance."""
        if self._user_service is None:
            self._user_service = UserService(self.session)
        return self._user_service
    
    @property
    def item_service(self) -> ItemService:
        """Get item service instance."""
        if self._item_service is None:
            self._item_service = ItemService(self.session)
        return self._item_service
    
    @property
    def email_service(self) -> EmailService:
        """Get email service instance."""
        if self._email_service is None:
            self._email_service = EmailService()
        return self._email_service


def get_service_container(
    session: Annotated[Session, Depends(get_session)]
) -> ServiceContainer:
    """Get service container with all dependencies."""
    return ServiceContainer(session)


# Type alias for service container dependency
ServiceContainerDep = Annotated[ServiceContainer, Depends(get_service_container)]