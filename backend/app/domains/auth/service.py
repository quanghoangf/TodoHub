"""Authentication service."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.security import ALGORITHM, verify_password
from app.domains.auth.schemas import LoginRequest, PasswordResetRequest, TokenResponse
from app.domains.users.models import User
from app.domains.users.repository import UserRepository


class AuthService:
    """Authentication service handling login and token operations."""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def login(self, login_data: LoginRequest) -> TokenResponse:
        """Login user and return access token."""
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise UnauthorizedError("Incorrect email or password")
        
        if not user.is_active:
            raise UnauthorizedError("Inactive user")
        
        access_token = self.create_access_token(subject=str(user.id))
        return TokenResponse(access_token=access_token)
    
    def create_access_token(self, subject: str) -> str:
        """Create JWT access token."""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {"exp": expire, "sub": subject}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> str:
        """Verify JWT token and return subject."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            token_subject: str = payload.get("sub")
            if token_subject is None:
                raise UnauthorizedError("Could not validate credentials")
            return token_subject
        except InvalidTokenError:
            raise UnauthorizedError("Could not validate credentials")
    
    def generate_password_reset_token(self, email: str) -> str:
        """Generate password reset token."""
        user = self.user_repository.get_by_email(email)
        if not user:
            # Don't reveal if email exists
            raise ValidationError("If that email exists, a reset link has been sent")
        
        delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        now = datetime.now(timezone.utc)
        expires = now + delta
        exp = expires.timestamp()
        
        encoded_jwt = jwt.encode(
            {"exp": exp, "nbf": now, "sub": email},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return encoded_jwt
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email."""
        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[ALGORITHM]
            )
            return str(decoded_token["sub"])
        except InvalidTokenError:
            return None