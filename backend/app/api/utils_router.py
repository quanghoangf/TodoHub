"""Utility routes."""

from fastapi import APIRouter

from app.core.container import ServiceContainerDep
from app.domains.shared.dependencies import CurrentUser
from app.domains.shared.schemas import MessageResponse

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
def health_check() -> bool:
    """Health check endpoint."""
    return True


@router.post("/test-email/", response_model=MessageResponse)
def test_email(
    container: ServiceContainerDep,
    current_user: CurrentUser
) -> MessageResponse:
    """Test email sending."""
    email_data = container.email_service.generate_test_email(current_user.email)
    container.email_service.send_email(
        email_to=current_user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    
    return MessageResponse(message=f"Test email sent to {current_user.email}")