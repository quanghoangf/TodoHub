"""Analytics API router."""

import uuid
from typing import Any

from fastapi import APIRouter, Query

from app.core.container import ServiceContainerDep
from app.domains.analytics.schemas import (
    DashboardResponse,
    ExportRequest,
    ExportResponse,
    HabitSummaryResponse,
    HeatmapResponse,
)
from app.domains.shared.dependencies import CurrentUser

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/habits/{habit_id}/heatmap", response_model=HeatmapResponse)
def get_habit_heatmap(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
    days_back: int = Query(
        default=365, ge=30, le=730, description="Number of days to include in heatmap"
    ),
) -> Any:
    """
    Get calendar heatmap data for a habit.

    Returns daily completion data for visualization in a calendar heatmap,
    similar to GitHub's contribution graph.
    """
    return container.analytics_service.get_habit_heatmap(
        habit_id, current_user, days_back
    )


@router.get("/habits/{habit_id}/summary", response_model=HabitSummaryResponse)
def get_habit_summary(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
) -> Any:
    """
    Get comprehensive analytics summary for a habit.

    Includes completion statistics, streak information, weekday patterns,
    monthly trends, and other performance metrics.
    """
    return container.analytics_service.get_habit_summary(habit_id, current_user)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_analytics(
    *,
    current_user: CurrentUser,
    container: ServiceContainerDep,
) -> Any:
    """
    Get dashboard analytics overview for the current user.

    Provides a high-level overview of all habits, completion rates,
    streaks, and recent activity patterns.
    """
    print('Hello here ')
    return container.analytics_service.get_user_dashboard(current_user)


@router.post("/exports/csv", response_model=ExportResponse)
def generate_csv_export(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    export_request: ExportRequest,
) -> Any:
    """
    Generate CSV export for habit completion data.

    Allows users to export their habit data for external analysis,
    backup, or migration to other systems.
    """
    return container.analytics_service.generate_csv_export(export_request, current_user)


@router.get("/exports/habits/{habit_id}/csv", response_model=ExportResponse)
def generate_habit_csv_export(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    habit_id: uuid.UUID,
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    include_metadata: bool = Query(True, description="Include habit metadata"),
) -> Any:
    """
    Generate CSV export for a specific habit.

    Convenience endpoint for exporting data for a single habit
    with optional date range filtering.
    """
    from datetime import datetime

    # Parse dates if provided
    parsed_start_date = None
    parsed_end_date = None

    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date format, will be handled by service

    if end_date:
        try:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date format, will be handled by service

    export_request = ExportRequest(
        habit_ids=[habit_id],
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        include_metadata=include_metadata,
    )

    return container.analytics_service.generate_csv_export(export_request, current_user)
