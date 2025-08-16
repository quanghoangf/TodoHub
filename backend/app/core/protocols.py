"""Service protocols/interfaces for dependency injection."""

import uuid
from typing import Protocol

from app.domains.auth.schemas import LoginRequest, TokenResponse
from app.domains.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.domains.shared.schemas import MessageResponse
from app.domains.users.models import User
from app.domains.users.schemas import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)


class AuthServiceProtocol(Protocol):
    """Auth service interface."""
    
    def login(self, login_data: LoginRequest) -> TokenResponse: ...
    def verify_token(self, token: str) -> str: ...
    def generate_password_reset_token(self, email: str) -> str: ...


class UserServiceProtocol(Protocol):
    """User service interface."""
    
    def get_users(self, skip: int = 0, limit: int = 100) -> UsersPublic: ...
    def get_user_by_id(self, user_id: uuid.UUID, current_user: User) -> UserPublic: ...
    def create_user(self, user_data: UserCreate) -> UserPublic: ...
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> UserPublic: ...
    def delete_user(self, user_id: uuid.UUID, current_user: User) -> MessageResponse: ...


class ItemServiceProtocol(Protocol):
    """Item service interface."""
    
    def get_items(self, current_user: User, skip: int = 0, limit: int = 100) -> ItemsPublic: ...
    def get_item_by_id(self, item_id: uuid.UUID, current_user: User) -> ItemPublic: ...
    def create_item(self, item_data: ItemCreate, current_user: User) -> ItemPublic: ...
    def update_item(self, item_id: uuid.UUID, item_data: ItemUpdate, current_user: User) -> ItemPublic: ...
    def delete_item(self, item_id: uuid.UUID, current_user: User) -> MessageResponse: ...