from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserUpdate
from app.domains.users.service import UserService
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user_service = UserService(db)
    user_public = user_service.create_user(user_in)
    # Return the actual User model for tests
    from app.domains.users.repository import UserRepository
    user_repo = UserRepository(db)
    return user_repo.get_or_404(user_public.id)


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    from app.domains.users.repository import UserRepository
    
    password = random_lower_string()
    user_repo = UserRepository(db)
    user_service = UserService(db)
    
    user = user_repo.get_by_email(email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user_public = user_service.create_user(user_in_create)
        user = user_repo.get_or_404(user_public.id)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        user_service.update_user(user.id, user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
