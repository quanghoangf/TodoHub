"""Authentication router."""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.container import ServiceContainerDep
from app.domains.auth.schemas import LoginRequest, PasswordResetRequest, TokenResponse
from app.domains.shared.schemas import MessageResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    container: ServiceContainerDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login for access token."""
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return container.auth_service.login(login_data)


@router.post("/password-recovery", response_model=MessageResponse)
def recover_password(
    container: ServiceContainerDep,
    password_reset: PasswordResetRequest
) -> MessageResponse:
    """Password Recovery."""
    # Generate reset token
    token = container.auth_service.generate_password_reset_token(password_reset.email)
    
    # Send reset email
    email_data = container.email_service.generate_reset_password_email(
        email_to=password_reset.email,
        email=password_reset.email,
        token=token
    )
    
    container.email_service.send_email(
        email_to=password_reset.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    
    return MessageResponse(message="Password recovery email sent")