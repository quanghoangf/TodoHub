"""Database initialization."""

from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate
from app.domains.users.service import UserService


def init_db() -> None:
    """Initialize database with default data."""
    with Session(engine) as session:
        # Check if superuser already exists
        statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
        user = session.exec(statement).first()
        
        if not user:
            # Create first superuser
            user_service = UserService(session)
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Super User",
                is_superuser=True,
                is_active=True,
            )
            user_service.create_user(user_in)
            print(f"Created superuser: {settings.FIRST_SUPERUSER}")
        else:
            print(f"Superuser already exists: {settings.FIRST_SUPERUSER}")