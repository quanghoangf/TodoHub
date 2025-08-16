"""Shared dependencies."""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlmodel import Session

from app.core.container import ServiceContainer, ServiceContainerDep, get_service_container
from app.core.database import get_session
from app.core.exceptions import UnauthorizedError
from app.domains.users.models import User
from app.domains.users.repository import UserRepository

# Security scheme
security = HTTPBearer()

# Type aliases for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    container: ServiceContainerDep,
    token: Annotated[str, Depends(security)]
) -> User:
    """Get current authenticated user."""
    try:
        # Use service from container
        auth_service = container.auth_service
        token_data = auth_service.verify_token(token.credentials)
        user_id = uuid.UUID(token_data)
        
        user_repository = UserRepository(container.session)
        user = user_repository.get(user_id)
        
        if not user:
            raise UnauthorizedError("User not found")
        
        return user
    except (UnauthorizedError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


# Type aliases for commonly used dependencies
CurrentUser = Annotated[User, Depends(get_current_active_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]