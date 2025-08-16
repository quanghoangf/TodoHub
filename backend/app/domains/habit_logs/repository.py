"""Habit logs repository."""

import uuid
from datetime import date
from typing import List, Optional

from sqlmodel import Session, select, and_, desc

from app.domains.habit_logs.models import HabitLog, StreakCache
from app.domains.habit_logs.schemas import HabitLogCreate, HabitLogPublic
from app.domains.shared.repository import BaseRepository


class HabitLogRepository(BaseRepository[HabitLog, HabitLogCreate, HabitLogPublic]):
    """Repository for habit log operations."""
    
    def __init__(self, session: Session):
        super().__init__(HabitLog, session)
    
    def get_by_habit_and_date(
        self, 
        habit_id: uuid.UUID, 
        local_date: date
    ) -> Optional[HabitLog]:
        """Get habit log by habit ID and local date."""
        query = select(HabitLog).where(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.local_date == local_date
            )
        )
        return self.session.exec(query).first()
    
    def get_by_habit(
        self, 
        habit_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[HabitLog]:
        """Get all logs for a specific habit."""
        query = select(HabitLog).where(
            HabitLog.habit_id == habit_id
        ).order_by(desc(HabitLog.local_date)).offset(skip).limit(limit)
        return list(self.session.exec(query).all())
    
    def get_by_user(
        self, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[HabitLog]:
        """Get all logs for a specific user."""
        query = select(HabitLog).where(
            HabitLog.user_id == user_id
        ).order_by(desc(HabitLog.local_date)).offset(skip).limit(limit)
        return list(self.session.exec(query).all())
    
    def get_streak_dates(self, habit_id: uuid.UUID) -> List[date]:
        """Get all logged dates for a habit, ordered by date."""
        query = select(HabitLog.local_date).where(
            HabitLog.habit_id == habit_id
        ).order_by(HabitLog.local_date)
        return list(self.session.exec(query).all())
    
    def count_by_habit(self, habit_id: uuid.UUID) -> int:
        """Count logs for a specific habit."""
        return self.count(filters={"habit_id": habit_id})
    
    def delete_by_habit_and_date(
        self, 
        habit_id: uuid.UUID, 
        local_date: date
    ) -> Optional[HabitLog]:
        """Delete habit log by habit ID and local date."""
        log = self.get_by_habit_and_date(habit_id, local_date)
        if log:
            self.session.delete(log)
            self.session.commit()
        return log


class StreakRepository:
    """Repository for streak cache operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_habit(self, habit_id: uuid.UUID) -> Optional[StreakCache]:
        """Get streak cache by habit ID."""
        return self.session.get(StreakCache, habit_id)
    
    def create_or_update(
        self, 
        habit_id: uuid.UUID, 
        current_streak: int, 
        longest_streak: int
    ) -> StreakCache:
        """Create or update streak cache."""
        streak_cache = self.get_by_habit(habit_id)
        
        if streak_cache:
            # Update existing cache
            streak_cache.current_streak = current_streak
            streak_cache.longest_streak = max(longest_streak, streak_cache.longest_streak)
            from datetime import datetime
            streak_cache.last_updated = datetime.utcnow()
        else:
            # Create new cache
            streak_cache = StreakCache(
                habit_id=habit_id,
                current_streak=current_streak,
                longest_streak=longest_streak
            )
            self.session.add(streak_cache)
        
        self.session.commit()
        self.session.refresh(streak_cache)
        return streak_cache
    
    def delete_by_habit(self, habit_id: uuid.UUID) -> Optional[StreakCache]:
        """Delete streak cache by habit ID."""
        streak_cache = self.get_by_habit(habit_id)
        if streak_cache:
            self.session.delete(streak_cache)
            self.session.commit()
        return streak_cache