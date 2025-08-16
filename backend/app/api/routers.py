"""API router configuration."""

from fastapi import APIRouter

from app.api.utils_router import router as utils_router
from app.core.config import settings
from app.domains.auth.router import router as auth_router
from app.domains.items.router import router as items_router
from app.domains.users.router import router as users_router

# Create main API router
api_router = APIRouter()

# Include domain routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(items_router)
api_router.include_router(utils_router)

# Include development-only routes
if settings.ENVIRONMENT == "local":
    # Add any development-specific routes here
    pass