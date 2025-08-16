"""Habit repository."""

import uuid
from typing import List

from sqlmodel import Session

from app.domains.habits.models import Habit
from app.domains.habits.schemas import HabitCreate, HabitUpdate
from app.domains.shared.repository import BaseRepository


class HabitRepository(BaseRepository[Habit, HabitCreate, HabitUpdate]):
    """Habit repository with habit-specific operations."""
    
    def __init__(self, session: Session):
        super().__init__(Habit, session)
    
    def get_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Habit]:
        """Get habits by owner ID."""
        return self.get_multi(skip=skip, limit=limit, filters={"owner_id": owner_id})
    
    def count_by_owner(self, owner_id: uuid.UUID) -> int:
        """Count habits by owner ID."""
        return self.count(filters={"owner_id": owner_id})