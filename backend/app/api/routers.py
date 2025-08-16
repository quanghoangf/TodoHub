"""API router configuration."""

from fastapi import APIRouter

from app.api.utils_router import router as utils_router
from app.core.config import settings
from app.domains.analytics.router import router as analytics_router
from app.domains.auth.router import router as auth_router
from app.domains.habits.router import router as habits_router
from app.domains.habit_logs.router import router as habit_logs_router
from app.domains.users.router import router as users_router

# Create main API router
api_router = APIRouter()

# Include domain routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(habits_router)
api_router.include_router(habit_logs_router, tags=["habit-logs"])
api_router.include_router(analytics_router, tags=["analytics"])
api_router.include_router(utils_router)

# Include development-only routes
if settings.ENVIRONMENT == "local":
    # Add any development-specific routes here
    pass