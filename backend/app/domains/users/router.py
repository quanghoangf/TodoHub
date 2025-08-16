"""Users router."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.core.container import ServiceContainerDep
from app.domains.shared.dependencies import CurrentSuperUser, CurrentUser, SessionDep
from app.domains.shared.schemas import MessageResponse
from app.domains.users.schemas import (
    UpdatePassword,
    UpdateTimezone,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersPublic)
def read_users(
    container: ServiceContainerDep,
    current_user: CurrentSuperUser, 
    skip: int = 0, 
    limit: int = 100
) -> Any:
    """Retrieve users. Requires superuser privileges."""
    return container.user_service.get_users(skip=skip, limit=limit)


@router.post("/", response_model=UserPublic)
def create_user(
    *, 
    container: ServiceContainerDep,
    current_user: CurrentSuperUser, 
    user_in: UserCreate
) -> Any:
    """Create new user. Requires superuser privileges."""
    user = container.user_service.create_user(user_in)
    
    # Send welcome email if email is configured
    try:
        email_data = container.email_service.generate_new_account_email(
            email_to=user_in.email, 
            username=user_in.email, 
            password=user_in.password
        )
        container.email_service.send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    except Exception:
        # Don't fail user creation if email fails
        pass
    
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, 
    container: ServiceContainerDep,
    user_in: UserUpdateMe, 
    current_user: CurrentUser
) -> Any:
    """Update own user."""
    return container.user_service.update_user_me(current_user, user_in)


@router.patch("/me/password", response_model=MessageResponse)
def update_password_me(
    *, 
    container: ServiceContainerDep,
    body: UpdatePassword, 
    current_user: CurrentUser
) -> Any:
    """Update own password."""
    return container.user_service.update_password(current_user, body)


@router.patch("/me/timezone", response_model=MessageResponse)
def update_timezone_me(
    *, 
    container: ServiceContainerDep,
    body: UpdateTimezone, 
    current_user: CurrentUser
) -> Any:
    """Update own timezone."""
    return container.user_service.update_timezone(current_user, body)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return UserPublic.model_validate(current_user)


@router.delete("/me", response_model=MessageResponse)
def delete_user_me(container: ServiceContainerDep, current_user: CurrentUser) -> Any:
    """Delete own user."""
    return container.user_service.delete_user_me(current_user)


@router.post("/signup", response_model=UserPublic)
def register_user(container: ServiceContainerDep, user_in: UserRegister) -> Any:
    """Create new user without authentication."""
    return container.user_service.register_user(user_in)


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, 
    container: ServiceContainerDep,
    current_user: CurrentUser
) -> Any:
    """Get a specific user by id."""
    return container.user_service.get_user_by_id(user_id, current_user)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *,
    container: ServiceContainerDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: CurrentSuperUser,
) -> Any:
    """Update a user. Requires superuser privileges."""
    return container.user_service.update_user(user_id, user_in)


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    container: ServiceContainerDep,
    current_user: CurrentSuperUser, 
    user_id: uuid.UUID
) -> MessageResponse:
    """Delete a user. Requires superuser privileges."""
    return container.user_service.delete_user(user_id, current_user)