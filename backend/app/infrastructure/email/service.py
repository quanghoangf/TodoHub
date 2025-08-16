"""Email service."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import emails  # type: ignore
from jinja2 import Template

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """Email data container."""
    
    html_content: str
    subject: str


class EmailService:
    """Email service for sending emails."""
    
    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates" / "build"
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context."""
        template_path = self.templates_path / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
        
        template_str = template_path.read_text()
        html_content = Template(template_str).render(context)
        return html_content
    
    def send_email(self, *, email_to: str, subject: str, html_content: str) -> None:
        """Send email."""
        if not settings.emails_enabled:
            logger.warning("Email sending is disabled")
            return
        
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )
        
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        elif settings.SMTP_SSL:
            smtp_options["ssl"] = True
        if settings.SMTP_USER:
            smtp_options["user"] = settings.SMTP_USER
        if settings.SMTP_PASSWORD:
            smtp_options["password"] = settings.SMTP_PASSWORD
        
        response = message.send(to=email_to, smtp=smtp_options)
        logger.info(f"Email sent to {email_to}: {response}")
    
    def generate_test_email(self, email_to: str) -> EmailData:
        """Generate test email."""
        subject = f"{settings.PROJECT_NAME} - Test email"
        html_content = self.render_template(
            "test_email.html",
            {"project_name": settings.PROJECT_NAME, "email": email_to},
        )
        return EmailData(html_content=html_content, subject=subject)
    
    def generate_reset_password_email(self, email_to: str, email: str, token: str) -> EmailData:
        """Generate password reset email."""
        subject = f"{settings.PROJECT_NAME} - Password recovery for user {email}"
        link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
        html_content = self.render_template(
            "reset_password.html",
            {
                "project_name": settings.PROJECT_NAME,
                "username": email,
                "email": email_to,
                "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
                "link": link,
            },
        )
        return EmailData(html_content=html_content, subject=subject)
    
    def generate_new_account_email(
        self, email_to: str, username: str, password: str
    ) -> EmailData:
        """Generate new account email."""
        subject = f"{settings.PROJECT_NAME} - New account for user {username}"
        html_content = self.render_template(
            "new_account.html",
            {
                "project_name": settings.PROJECT_NAME,
                "username": username,
                "password": password,
                "email": email_to,
                "link": settings.FRONTEND_HOST,
            },
        )
        return EmailData(html_content=html_content, subject=subject)