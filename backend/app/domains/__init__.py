"""Import all domain models to ensure SQLModel registration."""

# Import all models to ensure they are registered with SQLModel
from app.domains.habits.models import Habit  # noqa
from app.domains.habit_logs.models import HabitLog, StreakCache  # noqa
from app.domains.users.models import User  # noqa

__all__ = ["User", "Habit", "HabitLog", "StreakCache"]