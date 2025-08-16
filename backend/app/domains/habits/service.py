"""Habit service."""

import uuid

from sqlmodel import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domains.habits.models import Habit
from app.domains.habits.repository import HabitRepository
from app.domains.habits.schemas import HabitCreate, HabitPublic, HabitsPublic, HabitUpdate
from app.domains.shared.schemas import MessageResponse
from app.domains.users.models import User


class HabitService:
    """Habit service handling habit business logic."""
    
    def __init__(self, session: Session):
        self.session = session
        self.habit_repository = HabitRepository(session)
    
    def get_habits(self, current_user: User, skip: int = 0, limit: int = 100) -> HabitsPublic:
        """Get paginated list of habits."""
        if current_user.is_superuser:
            # Superusers can see all habits
            habits = self.habit_repository.get_multi(skip=skip, limit=limit)
            count = self.habit_repository.count()
        else:
            # Regular users can only see their own habits
            habits = self.habit_repository.get_by_owner(
                owner_id=current_user.id, skip=skip, limit=limit
            )
            count = self.habit_repository.count_by_owner(owner_id=current_user.id)
        
        return HabitsPublic(data=habits, count=count)
    
    def get_habit_by_id(self, habit_id: uuid.UUID, current_user: User) -> HabitPublic:
        """Get habit by ID with permission check."""
        habit = self.habit_repository.get_or_404(habit_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        return HabitPublic.model_validate(habit)
    
    def create_habit(self, habit_data: HabitCreate, current_user: User) -> HabitPublic:
        """Create new habit."""
        # Create habit with current user as owner
        habit_dict = habit_data.model_dump()
        habit_dict["owner_id"] = current_user.id
        
        db_habit = Habit(**habit_dict)
        self.session.add(db_habit)
        self.session.commit()
        self.session.refresh(db_habit)
        
        return HabitPublic.model_validate(db_habit)
    
    def update_habit(
        self, habit_id: uuid.UUID, habit_data: HabitUpdate, current_user: User
    ) -> HabitPublic:
        """Update habit by ID."""
        habit = self.habit_repository.get_or_404(habit_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        updated_habit = self.habit_repository.update(db_obj=habit, obj_in=habit_data)
        return HabitPublic.model_validate(updated_habit)
    
    def delete_habit(self, habit_id: uuid.UUID, current_user: User) -> MessageResponse:
        """Delete habit by ID."""
        habit = self.habit_repository.get_or_404(habit_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        self.habit_repository.delete(id=habit_id)
        return MessageResponse(message="Habit deleted successfully")