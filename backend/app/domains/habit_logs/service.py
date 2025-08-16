"""Habit logs service."""

import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from sqlmodel import Session

from app.core.exceptions import ValidationError, ForbiddenError, NotFoundError
from app.domains.habit_logs.models import HabitLog, StreakCache
from app.domains.habit_logs.repository import HabitLogRepository, StreakRepository
from app.domains.habit_logs.schemas import (
    HabitLogCreate, 
    HabitLogPublic, 
    HabitLogsPublic, 
    StreakResponse
)
from app.domains.habits.repository import HabitRepository
from app.domains.shared.schemas import MessageResponse
from app.domains.users.models import User


class HabitLogService:
    """Service for habit logging and streak calculation."""
    
    def __init__(self, session: Session):
        self.session = session
        self.habit_log_repository = HabitLogRepository(session)
        self.streak_repository = StreakRepository(session)
        self.habit_repository = HabitRepository(session)
    
    def log_habit(
        self, 
        habit_id: uuid.UUID, 
        log_data: HabitLogCreate, 
        current_user: User
    ) -> HabitLogPublic:
        """Log a habit completion with idempotency and streak calculation."""
        # Get habit and check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        # Check for existing log (idempotency)
        existing_log = self.habit_log_repository.get_by_habit_and_date(
            habit_id, log_data.local_date
        )
        if existing_log:
            # Return existing log if found
            return HabitLogPublic.model_validate(existing_log)
        
        # Validate date is not in the future (in user's timezone)
        user_tz = ZoneInfo(current_user.timezone)
        today_user_tz = datetime.now(user_tz).date()
        
        if log_data.local_date > today_user_tz:
            raise ValidationError("Cannot log habits for future dates")
        
        # Check backfill window if applicable
        if habit.backfill_window_hours > 0:
            # Convert hours to days for date comparison
            backfill_days = habit.backfill_window_hours // 24
            backfill_limit_date = today_user_tz - timedelta(days=backfill_days + 1)
            if log_data.local_date < backfill_limit_date:
                raise ValidationError(
                    f"Cannot log habits older than {habit.backfill_window_hours} hours"
                )
        
        # Create new log
        log_dict = log_data.model_dump()
        log_dict.update({
            "habit_id": habit_id,
            "user_id": current_user.id,
            "recorded_at": datetime.utcnow()
        })
        
        db_log = HabitLog(**log_dict)
        self.session.add(db_log)
        self.session.commit()
        self.session.refresh(db_log)
        
        # Recalculate and cache streak
        self._recalculate_streak(habit_id)
        
        return HabitLogPublic.model_validate(db_log)
    
    def get_habit_logs(
        self, 
        habit_id: uuid.UUID, 
        current_user: User, 
        skip: int = 0, 
        limit: int = 100
    ) -> HabitLogsPublic:
        """Get habit logs with permission check."""
        # Get habit and check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        logs = self.habit_log_repository.get_by_habit(habit_id, skip, limit)
        count = self.habit_log_repository.count_by_habit(habit_id)
        
        return HabitLogsPublic(
            data=[HabitLogPublic.model_validate(log) for log in logs],
            count=count
        )
    
    def get_habit_streak(
        self, 
        habit_id: uuid.UUID, 
        current_user: User
    ) -> StreakResponse:
        """Get habit streak information."""
        # Get habit and check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        # Try to get cached streak first
        streak_cache = self.streak_repository.get_by_habit(habit_id)
        
        if not streak_cache:
            # Calculate and cache streak if not found
            current_streak, longest_streak = self._calculate_streak(habit_id, current_user.timezone)
            streak_cache = self.streak_repository.create_or_update(
                habit_id, current_streak, longest_streak
            )
        
        return StreakResponse(
            habit_id=habit_id,
            current_streak=streak_cache.current_streak,
            longest_streak=streak_cache.longest_streak,
            last_updated=streak_cache.last_updated
        )
    
    def delete_habit_log(
        self, 
        habit_id: uuid.UUID, 
        local_date: date, 
        current_user: User
    ) -> MessageResponse:
        """Delete a habit log and recalculate streak."""
        # Get habit and check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        if not current_user.is_superuser and habit.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        # Delete the log
        deleted_log = self.habit_log_repository.delete_by_habit_and_date(
            habit_id, local_date
        )
        
        if not deleted_log:
            raise NotFoundError("Habit log not found for the specified date")
        
        # Recalculate streak after deletion
        self._recalculate_streak(habit_id)
        
        return MessageResponse(message="Habit log deleted successfully")
    
    def _recalculate_streak(self, habit_id: uuid.UUID) -> None:
        """Recalculate and cache streak for a habit."""
        # Get user timezone from habit owner
        habit = self.habit_repository.get_or_404(habit_id)
        user_timezone = habit.owner.timezone if habit.owner else "UTC"
        
        current_streak, longest_streak = self._calculate_streak(habit_id, user_timezone)
        self.streak_repository.create_or_update(habit_id, current_streak, longest_streak)
    
    def _calculate_streak(self, habit_id: uuid.UUID, user_timezone: str) -> tuple[int, int]:
        """Calculate current and longest streak for a habit."""
        # Get all logged dates for the habit
        logged_dates = self.habit_log_repository.get_streak_dates(habit_id)
        
        if not logged_dates:
            return 0, 0
        
        # Convert to user timezone to get "today"
        user_tz = ZoneInfo(user_timezone)
        today = datetime.now(user_tz).date()
        
        # Calculate current streak (consecutive days from today backwards)
        current_streak = 0
        check_date = today
        
        # Check if today or yesterday was logged (allow for flexibility)
        logged_dates_set = set(logged_dates)
        
        # Start from today or yesterday if today isn't logged
        if today not in logged_dates_set:
            check_date = today - timedelta(days=1)
        
        # Count consecutive days backwards
        while check_date in logged_dates_set:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        
        if logged_dates:
            # Sort dates and find longest consecutive sequence
            sorted_dates = sorted(logged_dates)
            
            for i, log_date in enumerate(sorted_dates):
                if i == 0:
                    temp_streak = 1
                else:
                    # Check if this date is consecutive to previous
                    prev_date = sorted_dates[i - 1]
                    if log_date == prev_date + timedelta(days=1):
                        temp_streak += 1
                    else:
                        # Reset streak
                        longest_streak = max(longest_streak, temp_streak)
                        temp_streak = 1
            
            # Don't forget the last streak
            longest_streak = max(longest_streak, temp_streak)
        
        return current_streak, longest_streak