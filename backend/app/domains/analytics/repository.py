"""Analytics repository with optimized queries."""

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import case, extract
from sqlmodel import Session, and_, func, select

from app.domains.habit_logs.models import HabitLog
from app.domains.habits.models import Habit


class AnalyticsRepository:
    """Repository for analytics queries and data aggregation."""

    def __init__(self, session: Session):
        self.session = session

    def get_habit_heatmap_data(
        self, habit_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[tuple[date, int]]:
        """Get daily completion counts for heatmap visualization."""
        query = (
            select(HabitLog.local_date, func.count(HabitLog.id).label("completions"))
            .where(
                and_(
                    HabitLog.habit_id == habit_id,
                    HabitLog.local_date >= start_date,
                    HabitLog.local_date <= end_date,
                )
            )
            .group_by(HabitLog.local_date)
            .order_by(HabitLog.local_date)
        )

        result = self.session.exec(query).all()
        return [(row.local_date, row.completions) for row in result]

    def get_habit_completion_stats(
        self, habit_id: uuid.UUID, start_date: date | None = None
    ) -> dict:
        """Get comprehensive completion statistics for a habit."""
        # Base query for habit logs
        base_query = select(HabitLog).where(HabitLog.habit_id == habit_id)

        if start_date:
            base_query = base_query.where(HabitLog.local_date >= start_date)

        # Get all logs for the habit
        logs = list(self.session.exec(base_query).all())

        if not logs:
            return {
                "total_completions": 0,
                "completion_rate": 0.0,
                "first_completion": None,
                "last_completion": None,
                "unique_days": 0,
            }

        # Calculate basic stats
        total_completions = len(logs)
        unique_dates = set(log.local_date for log in logs)
        unique_days = len(unique_dates)

        first_completion = min(log.local_date for log in logs)
        last_completion = max(log.local_date for log in logs)

        # Calculate completion rate
        if start_date:
            total_possible_days = (datetime.now().date() - start_date).days + 1
        else:
            total_possible_days = (last_completion - first_completion).days + 1

        completion_rate = (
            unique_days / total_possible_days if total_possible_days > 0 else 0.0
        )

        return {
            "total_completions": total_completions,
            "completion_rate": min(completion_rate, 1.0),  # Cap at 100%
            "first_completion": first_completion,
            "last_completion": last_completion,
            "unique_days": unique_days,
            "total_possible_days": total_possible_days,
        }

    def get_weekday_completion_stats(self, habit_id: uuid.UUID) -> dict[str, int]:
        """Get completion counts by day of week."""
        query = (
            select(
                extract("dow", HabitLog.local_date).label("day_of_week"),
                func.count(HabitLog.id).label("completions"),
            )
            .where(HabitLog.habit_id == habit_id)
            .group_by(extract("dow", HabitLog.local_date))
        )

        result = self.session.exec(query).all()

        # Convert PostgreSQL day of week (0=Sunday) to our format
        dow_mapping = {
            0: "sunday",
            1: "monday",
            2: "tuesday",
            3: "wednesday",
            4: "thursday",
            5: "friday",
            6: "saturday",
        }

        weekday_stats = {day: 0 for day in dow_mapping.values()}

        for row in result:
            day_name = dow_mapping.get(int(row.day_of_week))
            if day_name:
                weekday_stats[day_name] = row.completions

        return weekday_stats

    def get_monthly_completion_trends(
        self, habit_id: uuid.UUID, months_back: int = 12
    ) -> list[dict]:
        """Get monthly completion trends for the specified number of months."""
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=months_back * 31)

        query = (
            select(
                func.date_trunc("month", HabitLog.local_date).label("month"),
                func.count(HabitLog.id).label("completions"),
                func.count(func.distinct(HabitLog.local_date)).label("unique_days"),
            )
            .where(
                and_(
                    HabitLog.habit_id == habit_id,
                    HabitLog.local_date >= start_date,
                    HabitLog.local_date <= end_date,
                )
            )
            .group_by(func.date_trunc("month", HabitLog.local_date))
            .order_by(func.date_trunc("month", HabitLog.local_date))
        )

        result = self.session.exec(query).all()

        trends = []
        for row in result:
            month_date = row.month.date() if hasattr(row.month, "date") else row.month
            month_str = month_date.strftime("%Y-%m")

            # Calculate days in month for completion rate
            if month_date.month == 12:
                next_month = month_date.replace(year=month_date.year + 1, month=1)
            else:
                next_month = month_date.replace(month=month_date.month + 1)

            days_in_month = (next_month - month_date).days
            completion_rate = (
                row.unique_days / days_in_month if days_in_month > 0 else 0.0
            )

            trends.append(
                {
                    "month": month_str,
                    "completions": row.completions,
                    "completion_rate": min(completion_rate, 1.0),
                }
            )

        return trends

    def get_user_habits_overview(self, user_id: uuid.UUID) -> list[dict]:
        """Get overview statistics for all user habits."""
        # Get habits with recent activity (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        seven_days_ago = datetime.now().date() - timedelta(days=7)

        query = (
            select(
                Habit.id,
                Habit.title,
                Habit.category,
                func.count(
                    case((HabitLog.local_date >= thirty_days_ago, HabitLog.id))
                ).label("completions_30_days"),
                func.count(
                    func.distinct(
                        case(
                            (
                                HabitLog.local_date >= thirty_days_ago,
                                HabitLog.local_date,
                            )
                        )
                    )
                ).label("unique_days_30"),
                func.count(
                    case((HabitLog.local_date >= seven_days_ago, HabitLog.id))
                ).label("completions_7_days"),
                func.max(HabitLog.local_date).label("last_completed"),
            )
            .select_from(Habit.__table__.outerjoin(HabitLog.__table__))
            .where(Habit.owner_id == user_id)
            .group_by(Habit.id, Habit.title, Habit.category)
            .order_by(Habit.title)
        )

        result = self.session.exec(query).all()

        habits_overview = []
        for row in result:
            completion_rate_30_days = (
                row.unique_days_30 / 30.0 if row.unique_days_30 else 0.0
            )

            habits_overview.append(
                {
                    "habit_id": row.id,
                    "title": row.title,
                    "category": row.category,
                    "completion_rate_30_days": min(completion_rate_30_days, 1.0),
                    "weekly_completions": row.completions_7_days or 0,
                    "last_completed": row.last_completed,
                }
            )

        return habits_overview

    def get_user_dashboard_stats(self, user_id: uuid.UUID) -> dict:
        """Get overall dashboard statistics for a user."""
        # Count total habits
        total_habits_query = select(func.count(Habit.id)).where(
            Habit.owner_id == user_id
        )
        total_habits = self.session.exec(total_habits_query).one()

        # Count active habits (with completions in last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)

        active_habits_query = (
            select(func.count(func.distinct(Habit.id)))
            .select_from(Habit.__table__.join(HabitLog.__table__))
            .where(
                and_(Habit.owner_id == user_id, HabitLog.local_date >= thirty_days_ago)
            )
        )
        active_habits = self.session.exec(active_habits_query).one() or 0

        # Total completions
        total_completions_query = (
            select(func.count(HabitLog.id))
            .select_from(HabitLog.__table__.join(Habit.__table__))
            .where(Habit.owner_id == user_id)
        )
        total_completions = self.session.exec(total_completions_query).one() or 0

        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "total_completions": total_completions,
        }

    def get_habits_for_export(
        self,
        user_id: uuid.UUID,
        habit_ids: list[uuid.UUID] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        """Get habit logs data for CSV export."""
        query = (
            select(
                Habit.title,
                Habit.category,
                Habit.description,
                HabitLog.local_date,
                HabitLog.recorded_at,
                HabitLog.meta,
            )
            .select_from(Habit.__table__.join(HabitLog.__table__))
            .where(Habit.owner_id == user_id)
        )

        if habit_ids:
            query = query.where(Habit.id.in_(habit_ids))

        if start_date:
            query = query.where(HabitLog.local_date >= start_date)

        if end_date:
            query = query.where(HabitLog.local_date <= end_date)

        query = query.order_by(HabitLog.local_date.desc(), Habit.title)

        result = self.session.exec(query).all()

        export_data = []
        for row in result:
            export_data.append(
                {
                    "habit_title": row.title,
                    "category": row.category or "",
                    "description": row.description or "",
                    "completion_date": row.local_date,
                    "recorded_at": row.recorded_at,
                    "metadata": row.meta or {},
                }
            )

        return export_data
