"""User service."""

import uuid
from typing import Dict, List, Optional

from sqlmodel import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.security import get_password_hash, verify_password
from app.domains.shared.schemas import MessageResponse
from app.domains.users.models import User
from app.domains.users.repository import UserRepository
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


class UserService:
    """User service handling user business logic."""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> UsersPublic:
        """Get paginated list of users."""
        users = self.user_repository.get_multi(skip=skip, limit=limit)
        count = self.user_repository.count()
        return UsersPublic(data=users, count=count)
    
    def get_user_by_id(self, user_id: uuid.UUID, current_user: User) -> UserPublic:
        """Get user by ID with permission check."""
        user = self.user_repository.get_or_404(user_id)
        
        # Users can see their own profile, superusers can see any profile
        if user == current_user or current_user.is_superuser:
            return UserPublic.model_validate(user)
        
        raise ForbiddenError("Not enough permissions")
    
    def create_user(self, user_data: UserCreate) -> UserPublic:
        """Create new user."""
        # Check if user with this email already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError("User with this email already exists")
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        db_user = User(**user_dict)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        
        return UserPublic.model_validate(db_user)
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> UserPublic:
        """Update user by ID."""
        db_user = self.user_repository.get_or_404(user_id)
        
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != db_user.email:
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ConflictError("User with this email already exists")
        
        # Handle password update
        update_dict = user_data.model_dump(exclude_unset=True)
        if "password" in update_dict:
            hashed_password = get_password_hash(update_dict["password"])
            update_dict["hashed_password"] = hashed_password
            del update_dict["password"]
        
        updated_user = self.user_repository.update(db_obj=db_user, obj_in=update_dict)
        return UserPublic.model_validate(updated_user)
    
    def update_user_me(self, current_user: User, user_data: UserUpdateMe) -> UserPublic:
        """Update current user's own profile."""
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != current_user.email:
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ConflictError("User with this email already exists")
        
        update_dict = user_data.model_dump(exclude_unset=True)
        updated_user = self.user_repository.update(db_obj=current_user, obj_in=update_dict)
        return UserPublic.model_validate(updated_user)
    
    def update_password(self, current_user: User, password_data: UpdatePassword) -> MessageResponse:
        """Update user's password."""
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise ValidationError("Incorrect password")
        
        # Check if new password is different
        if password_data.current_password == password_data.new_password:
            raise ValidationError("New password cannot be the same as the current one")
        
        # Update password
        hashed_password = get_password_hash(password_data.new_password)
        self.user_repository.update(
            db_obj=current_user, 
            obj_in={"hashed_password": hashed_password}
        )
        
        return MessageResponse(message="Password updated successfully")
    
    def delete_user(self, user_id: uuid.UUID, current_user: User) -> MessageResponse:
        """Delete user by ID."""
        user = self.user_repository.get_or_404(user_id)
        
        # Prevent superusers from deleting themselves
        if user == current_user and current_user.is_superuser:
            raise ForbiddenError("Super users are not allowed to delete themselves")
        
        self.user_repository.delete(id=user_id)
        return MessageResponse(message="User deleted successfully")
    
    def delete_user_me(self, current_user: User) -> MessageResponse:
        """Delete current user's own account."""
        # Prevent superusers from deleting themselves
        if current_user.is_superuser:
            raise ForbiddenError("Super users are not allowed to delete themselves")
        
        self.user_repository.delete(id=current_user.id)
        return MessageResponse(message="User deleted successfully")
    
    def register_user(self, user_data: UserRegister) -> UserPublic:
        """Register new user (public registration)."""
        # Check if user with this email already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError("User with this email already exists")
        
        # Create user with default permissions
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            timezone=user_data.timezone,
            is_active=True,
            is_superuser=False
        )
        
        return self.create_user(user_create)
    
    def update_timezone(self, current_user: User, timezone_data: UpdateTimezone) -> MessageResponse:
        """Update user's timezone."""
        self.user_repository.update(
            db_obj=current_user, 
            obj_in={"timezone": timezone_data.timezone}
        )
        
        return MessageResponse(message="Timezone updated successfully")