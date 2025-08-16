"""Analytics domain schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class HeatmapDataPoint(BaseModel):
    """Single data point for calendar heatmap."""

    date_value: date = Field(..., alias="date", description="Date of the data point")
    value: int = Field(..., description="Number of habits completed on this date")
    level: int = Field(..., description="Intensity level (0-4) for heatmap coloring")


class HeatmapResponse(BaseModel):
    """Calendar heatmap data for a habit."""

    habit_id: uuid.UUID
    start_date: date
    end_date: date
    data: list[HeatmapDataPoint] = Field(..., description="Daily completion data")
    total_days: int = Field(..., description="Total days in the period")
    completed_days: int = Field(..., description="Number of days with completions")


class CompletionStats(BaseModel):
    """Completion statistics for a habit."""

    total_completions: int = Field(..., description="Total number of completions")
    completion_rate: float = Field(..., description="Overall completion rate (0-1)")
    current_streak: int = Field(..., description="Current consecutive days")
    longest_streak: int = Field(..., description="Longest streak ever")
    average_completions_per_week: float = Field(
        ..., description="Average weekly completions"
    )


class WeekdayStats(BaseModel):
    """Statistics by day of week."""

    monday: int = Field(default=0, description="Completions on Monday")
    tuesday: int = Field(default=0, description="Completions on Tuesday")
    wednesday: int = Field(default=0, description="Completions on Wednesday")
    thursday: int = Field(default=0, description="Completions on Thursday")
    friday: int = Field(default=0, description="Completions on Friday")
    saturday: int = Field(default=0, description="Completions on Saturday")
    sunday: int = Field(default=0, description="Completions on Sunday")


class MonthlyTrend(BaseModel):
    """Monthly trend data point."""

    month: str = Field(..., description="Month in YYYY-MM format")
    completions: int = Field(..., description="Number of completions in the month")
    completion_rate: float = Field(..., description="Completion rate for the month")


class HabitSummaryResponse(BaseModel):
    """Comprehensive habit analytics summary."""

    habit_id: uuid.UUID
    habit_title: str
    habit_category: str | None
    start_date: date | None
    completion_stats: CompletionStats
    weekday_stats: WeekdayStats
    monthly_trends: list[MonthlyTrend] = Field(
        ..., description="Last 12 months of data"
    )
    best_streak_period: dict[str, date] | None = Field(
        default=None, description="Start and end dates of the longest streak"
    )


class DashboardHabitOverview(BaseModel):
    """Overview data for a habit on the dashboard."""

    habit_id: uuid.UUID
    title: str
    category: str | None
    current_streak: int
    completion_rate_30_days: float = Field(
        ..., description="Completion rate for last 30 days"
    )
    last_completed: date | None = Field(
        ..., description="Most recent completion date"
    )
    weekly_completions: int = Field(..., description="Completions in the last 7 days")


class DashboardResponse(BaseModel):
    """Dashboard analytics overview."""

    user_id: uuid.UUID
    total_habits: int
    active_habits: int = Field(
        ..., description="Habits with completions in last 30 days"
    )
    total_completions: int
    average_completion_rate: float = Field(
        ..., description="Average completion rate across all habits"
    )
    longest_current_streak: int = Field(
        ..., description="Longest current streak across all habits"
    )
    habits_overview: list[DashboardHabitOverview]
    completion_trends: list[MonthlyTrend] = Field(
        ..., description="Overall completion trends"
    )


class ExportRequest(BaseModel):
    """Request for CSV export."""

    habit_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="Specific habit IDs to export, or None for all user habits",
    )
    start_date: date | None = Field(
        default=None, description="Start date for export range"
    )
    end_date: date | None = Field(
        default=None, description="End date for export range"
    )
    include_metadata: bool = Field(
        default=True, description="Whether to include habit metadata in export"
    )


class ExportResponse(BaseModel):
    """Response for CSV export."""

    download_url: str = Field(..., description="URL to download the CSV file")
    filename: str = Field(..., description="Generated filename")
    total_records: int = Field(..., description="Number of records in the export")
    generated_at: datetime = Field(..., description="When the export was generated")
