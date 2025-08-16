"""Analytics service with business logic and caching."""

import csv
import io
import uuid
from datetime import datetime, timedelta

from sqlmodel import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domains.analytics.repository import AnalyticsRepository
from app.domains.analytics.schemas import (
    CompletionStats,
    DashboardHabitOverview,
    DashboardResponse,
    ExportRequest,
    ExportResponse,
    HabitSummaryResponse,
    HeatmapDataPoint,
    HeatmapResponse,
    MonthlyTrend,
    WeekdayStats,
)
from app.domains.habit_logs.repository import StreakRepository
from app.domains.habits.repository import HabitRepository
from app.domains.users.models import User


class AnalyticsService:
    """Service for analytics calculations and data processing."""

    def __init__(self, session: Session):
        self.session = session
        self.analytics_repository = AnalyticsRepository(session)
        self.habit_repository = HabitRepository(session)
        self.streak_repository = StreakRepository(session)

    def get_habit_heatmap(
        self, habit_id: uuid.UUID, current_user: User, days_back: int = 365
    ) -> HeatmapResponse:
        """Generate calendar heatmap data for a habit."""
        # Check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        # if not current_user.is_superuser and habit.owner_id != current_user.id:
        #     raise ForbiddenError("Not enough permissions")

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back - 1)

        # Get completion data
        completion_data = self.analytics_repository.get_habit_heatmap_data(
            habit_id, start_date, end_date
        )

        # Create a dictionary for quick lookup
        completion_dict = {date_val: count for date_val, count in completion_data}

        # Generate heatmap data points for all days in range
        heatmap_data = []
        current_date = start_date

        while current_date <= end_date:
            completions = completion_dict.get(current_date, 0)

            # Calculate intensity level (0-4) based on completions
            # Assuming max 1 completion per day for habits, but handling multiple
            if completions == 0:
                level = 0
            elif completions == 1:
                level = 3
            else:
                level = 4  # Multiple completions

            heatmap_data.append(
                HeatmapDataPoint(
                    date_value=current_date, value=completions, level=level
                )
            )

            current_date += timedelta(days=1)

        # Calculate summary statistics
        total_days = len(heatmap_data)
        completed_days = len([d for d in heatmap_data if d.value > 0])

        return HeatmapResponse(
            habit_id=habit_id,
            start_date=start_date,
            end_date=end_date,
            data=heatmap_data,
            total_days=total_days,
            completed_days=completed_days,
        )

    def get_habit_summary(
        self, habit_id: uuid.UUID, current_user: User
    ) -> HabitSummaryResponse:
        """Get comprehensive analytics summary for a habit."""
        # Check permissions
        habit = self.habit_repository.get_or_404(habit_id)
        # if not current_user.is_superuser and habit.owner_id != current_user.id:
        #     raise ForbiddenError("Not enough permissions")

        # Get completion statistics
        completion_stats_data = self.analytics_repository.get_habit_completion_stats(
            habit_id
        )

        # Get streak information
        streak_cache = self.streak_repository.get_by_habit(habit_id)
        current_streak = streak_cache.current_streak if streak_cache else 0
        longest_streak = streak_cache.longest_streak if streak_cache else 0

        # Calculate average completions per week
        if completion_stats_data["total_possible_days"] > 0:
            weeks = completion_stats_data["total_possible_days"] / 7.0
            avg_completions_per_week = (
                completion_stats_data["total_completions"] / weeks if weeks > 0 else 0.0
            )
        else:
            avg_completions_per_week = 0.0

        completion_stats = CompletionStats(
            total_completions=completion_stats_data["total_completions"],
            completion_rate=completion_stats_data["completion_rate"],
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_completions_per_week=avg_completions_per_week,
        )

        # Get weekday statistics
        weekday_data = self.analytics_repository.get_weekday_completion_stats(habit_id)
        weekday_stats = WeekdayStats(**weekday_data)

        # Get monthly trends
        monthly_data = self.analytics_repository.get_monthly_completion_trends(habit_id)
        monthly_trends = [MonthlyTrend(**month) for month in monthly_data]

        # Calculate best streak period (simplified - would need more complex logic for exact dates)
        best_streak_period = None
        if longest_streak > 0 and completion_stats_data["last_completion"]:
            # This is a simplified calculation - in a real implementation,
            # you'd want to find the actual dates of the longest streak
            best_streak_period = {
                "start": completion_stats_data["last_completion"]
                - timedelta(days=longest_streak),
                "end": completion_stats_data["last_completion"],
            }

        return HabitSummaryResponse(
            habit_id=habit_id,
            habit_title=habit.title,
            habit_category=habit.category,
            start_date=habit.start_date,
            completion_stats=completion_stats,
            weekday_stats=weekday_stats,
            monthly_trends=monthly_trends,
            best_streak_period=best_streak_period,
        )

    def get_user_dashboard(self, current_user: User) -> DashboardResponse:
        """Get dashboard analytics overview for a user."""
        # Get overall dashboard statistics
        dashboard_stats = self.analytics_repository.get_user_dashboard_stats(
            current_user.id
        )

        # Get habits overview
        habits_overview_data = self.analytics_repository.get_user_habits_overview(
            current_user.id
        )

        # Add current streak data to each habit
        habits_overview = []
        longest_current_streak = 0

        for habit_data in habits_overview_data:
            # Get current streak for this habit
            streak_cache = self.streak_repository.get_by_habit(habit_data["habit_id"])
            current_streak = streak_cache.current_streak if streak_cache else 0

            longest_current_streak = max(longest_current_streak, current_streak)

            habits_overview.append(
                DashboardHabitOverview(
                    habit_id=habit_data["habit_id"],
                    title=habit_data["title"],
                    category=habit_data["category"],
                    current_streak=current_streak,
                    completion_rate_30_days=habit_data["completion_rate_30_days"],
                    last_completed=habit_data["last_completed"],
                    weekly_completions=habit_data["weekly_completions"],
                )
            )

        # Calculate average completion rate
        if habits_overview:
            avg_completion_rate = sum(
                h.completion_rate_30_days for h in habits_overview
            ) / len(habits_overview)
        else:
            avg_completion_rate = 0.0

        # Get overall completion trends (simplified - aggregate all habits)
        # This could be enhanced to show user-wide trends
        completion_trends = [
            MonthlyTrend(
                month=datetime.now().strftime("%Y-%m"),
                completions=sum(h.weekly_completions for h in habits_overview)
                * 4,  # Rough estimate
                completion_rate=avg_completion_rate,
            )
        ]

        return DashboardResponse(
            user_id=current_user.id,
            total_habits=dashboard_stats["total_habits"],
            active_habits=dashboard_stats["active_habits"],
            total_completions=dashboard_stats["total_completions"],
            average_completion_rate=avg_completion_rate,
            longest_current_streak=longest_current_streak,
            habits_overview=habits_overview,
            completion_trends=completion_trends,
        )

    def generate_csv_export(
        self, export_request: ExportRequest, current_user: User
    ) -> ExportResponse:
        """Generate CSV export for habit data."""
        # Get data for export
        export_data = self.analytics_repository.get_habits_for_export(
            user_id=current_user.id,
            habit_ids=export_request.habit_ids,
            start_date=export_request.start_date,
            end_date=export_request.end_date,
        )

        if not export_data:
            raise NotFoundError("No data found for export criteria")

        # Generate CSV content
        output = io.StringIO()

        # Define CSV headers
        headers = ["Habit Title", "Category", "Completion Date", "Recorded At"]

        if export_request.include_metadata:
            headers.extend(["Description", "Metadata"])

        writer = csv.writer(output)
        writer.writerow(headers)

        # Write data rows
        for row in export_data:
            csv_row = [
                row["habit_title"],
                row["category"],
                row["completion_date"].strftime("%Y-%m-%d"),
                row["recorded_at"].strftime("%Y-%m-%d %H:%M:%S"),
            ]

            if export_request.include_metadata:
                csv_row.extend(
                    [
                        row["description"],
                        str(row["metadata"]) if row["metadata"] else "",
                    ]
                )

            writer.writerow(csv_row)

        csv_content = output.getvalue()
        output.close()

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"habits_export_{current_user.id}_{timestamp}.csv"

        # In a real implementation, you would:
        # 1. Save the CSV to a temporary file or cloud storage
        # 2. Generate a secure download URL
        # 3. Optionally set up background cleanup of old files

        # For now, we'll create a simple data URL (not suitable for large files)
        import base64

        csv_b64 = base64.b64encode(csv_content.encode()).decode()
        download_url = f"data:text/csv;base64,{csv_b64}"

        return ExportResponse(
            download_url=download_url,
            filename=filename,
            total_records=len(export_data),
            generated_at=datetime.now(),
        )
